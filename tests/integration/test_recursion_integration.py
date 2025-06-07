"""
Tests de integración para el escenario completo de prevención de recursión
"""

import pytest

# Implements Dart AI Task: Skip tests if PyQt6 is missing
pytest.importorskip("PyQt6")

import time
import sqlite3
from unittest.mock import patch, Mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

import sys
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.database.connection import DatabaseConnection, DatabaseConnectionError
from src.ui.windows.main_window import MainWindow
from src.services.music_service import MusicService


class TestRecursionIntegration:
    """Tests de integración para el escenario completo de recursión"""
    
    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Crear una base de datos temporal para tests"""
        db_path = tmp_path / "test.db"
        return str(db_path)
    
    @pytest.fixture
    def db_connection(self, temp_db_path):
        """Crear conexión de base de datos para tests"""
        db = DatabaseConnection(temp_db_path)
        # Crear tabla de songs básica para tests
        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    genre TEXT,
                    bpm INTEGER,
                    file_path TEXT UNIQUE NOT NULL
                )
            """)
        return db
    
    @pytest.fixture
    def main_window_with_real_db(self, qtbot, db_connection):
        """MainWindow con base de datos real pero servicios de audio mockeados"""
        with patch('src.ui.windows.main_window.AudioService') as mock_audio_service:
            window = MainWindow(db_connection)
            qtbot.addWidget(window)
            return window
    
    def test_full_search_flow_with_db_error(self, main_window_with_real_db, qtbot, temp_db_path):
        """Test del flujo completo de búsqueda con error de base de datos"""
        window = main_window_with_real_db
        
        # Simular error de base de datos eliminando el archivo
        Path(temp_db_path).unlink()  # Eliminar archivo de DB
        
        # Contador para detectar recursión
        call_count = 0
        original_method = window.load_songs_for_library_view
        
        def counting_wrapper(page):
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                pytest.fail(f"Recursión detectada: load_songs_for_library_view llamado {call_count} veces")
            return original_method(page)
        
        window.load_songs_for_library_view = counting_wrapper
        
        # Disparar búsqueda que debería fallar
        window.library_view.search_field.setText("test search")
        
        # Esperar que el debouncing termine
        qtbot.wait(400)
        
        # Verificar que solo se llamó una vez debido al circuit breaker
        assert call_count == 1
        
        # Verificar que el circuit breaker está activo
        assert not window._loading_circuit_breaker.can_execute()
        
        # Intentar otra búsqueda - debe ser bloqueada
        call_count = 0  # Reset counter
        window.library_view.search_field.setText("another search")
        qtbot.wait(400)
        
        # No debe haber nuevas llamadas
        assert call_count == 0
    
    def test_recovery_after_db_restoration(self, main_window_with_real_db, qtbot, db_connection, temp_db_path):
        """Test de recuperación automática cuando la DB vuelve a estar disponible"""
        window = main_window_with_real_db
        
        # Primero, causar un error eliminando la DB
        Path(temp_db_path).unlink()
        
        # Disparar búsqueda que falle
        window.library_view.search_field.setText("test")
        qtbot.wait(400)
        
        # Verificar que está en estado de error
        assert not window._loading_circuit_breaker.can_execute()
        
        # "Restaurar" la base de datos recreándola
        with db_connection.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    genre TEXT,
                    bpm INTEGER,
                    file_path TEXT UNIQUE NOT NULL
                )
            """)
            # Insertar datos de prueba
            conn.execute("""
                INSERT INTO songs (title, artist, album, genre, file_path)
                VALUES ('Test Song', 'Test Artist', 'Test Album', 'Test Genre', '/test/path.mp3')
            """)
        
        # Reset del estado de error manualmente
        window.reset_loading_errors()
        
        # Ahora debe permitir búsquedas nuevamente
        assert window._loading_circuit_breaker.can_execute()
        
        # Disparar nueva búsqueda que debe funcionar
        window.library_view.search_field.setText("Test Song")
        qtbot.wait(400)
        
        # Verificar que el estado es exitoso
        assert window._loading_circuit_breaker.can_execute()
    
    def test_ui_remains_responsive_during_errors(self, main_window_with_real_db, qtbot, temp_db_path):
        """Test que la UI permanece responsiva durante errores"""
        window = main_window_with_real_db
        
        # Simular DB error
        Path(temp_db_path).unlink()
        
        # Disparar múltiples búsquedas rápidamente
        search_texts = ["search1", "search2", "search3", "search4"]
        
        for text in search_texts:
            window.library_view.search_field.setText(text)
            qtbot.wait(50)  # Búsquedas rápidas
        
        # Esperar que el debouncing termine
        qtbot.wait(400)
        
        # La UI debe seguir respondiendo - verificar que podemos interactuar
        # con otros elementos sin bloqueos
        assert window.isVisible()
        assert window.library_view.isEnabled()
        
        # El status bar debe mostrar un mensaje de error amigable
        status_text = window.statusBar().currentMessage()
        assert "error" in status_text.lower() or "Error" in status_text
        
        # No debe haber QMessageBox modal bloqueando la UI
        # (Esto es importante - las ventanas modales causaban el problema original)
    
    def test_debouncing_prevents_excessive_db_calls(self, main_window_with_real_db, qtbot):
        """Test que el debouncing previene llamadas excesivas a la DB"""
        window = main_window_with_real_db
        
        # Contador de llamadas al servicio de música
        call_count = 0
        original_search = window.music_service.search_songs
        
        def counting_search(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_search(*args, **kwargs)
        
        window.music_service.search_songs = counting_search
        
        # Simular typing rápido (múltiples cambios en poco tiempo)
        search_texts = ["t", "te", "tes", "test", "test ", "test s", "test so", "test song"]
        
        for text in search_texts:
            window.library_view.search_field.setText(text)
            window.library_view.on_search_changed()
            qtbot.wait(50)  # Cambios más rápidos que el debounce delay
        
        # Esperar que el debouncing termine
        qtbot.wait(400)
        
        # Debe haber hecho solo UNA llamada al final debido al debouncing
        assert call_count <= 1  # Máximo 1 llamada debido al debouncing
    
    def test_circuit_breaker_resets_after_cooldown(self, main_window_with_real_db, qtbot, temp_db_path):
        """Test que el circuit breaker se resetea automáticamente después del cooldown"""
        window = main_window_with_real_db
        
        # Configurar cooldown corto para test rápido
        window._loading_circuit_breaker._cooldown = 0.2  # 200ms
        
        # Causar error
        Path(temp_db_path).unlink()
        window.library_view.search_field.setText("test")
        qtbot.wait(400)
        
        # Verificar que está bloqueado
        assert not window._loading_circuit_breaker.can_execute()
        
        # Esperar el cooldown
        qtbot.wait(250)  # 250ms > 200ms cooldown
        
        # Ahora debe permitir nuevas operaciones
        assert window._loading_circuit_breaker.can_execute()


# Configuración de pytest
if __name__ == "__main__":
    pytest.main([__file__])
