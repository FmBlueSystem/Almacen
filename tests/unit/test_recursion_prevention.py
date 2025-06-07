"""
Tests para prevenir regresión del RecursionError en la aplicación
"""

import pytest

# Implements Dart AI Task: Skip tests if PyQt6 is missing
pytest.importorskip("PyQt6")

import time
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

import sys
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.utils.error_handler import LoadingCircuitBreaker, DebouncedEmitter, ErrorHandler
from src.database.connection import DatabaseConnection, DatabaseConnectionError, DatabaseTimeoutError
from src.ui.windows.main_window import MainWindow
from src.ui.components.content_views.library_view import LibraryView


class TestLoadingCircuitBreaker:
    """Tests para el LoadingCircuitBreaker"""
    
    def test_circuit_breaker_prevents_concurrent_loading(self):
        """Test que el circuit breaker previene carga concurrente"""
        breaker = LoadingCircuitBreaker(cooldown=1.0)
        
        # Primera carga debe ser permitida
        assert breaker.can_execute() is True
        assert breaker.start_loading() is True
        
        # Segunda carga inmediata debe ser bloqueada
        assert breaker.can_execute() is False
        assert breaker.start_loading() is False
        
        # Terminar la primera carga
        breaker.finish_loading(success=True)
        
        # Ahora debe permitir nueva carga
        assert breaker.can_execute() is True
    
    def test_circuit_breaker_cooldown_after_error(self):
        """Test que el circuit breaker respeta el cooldown después de error"""
        breaker = LoadingCircuitBreaker(cooldown=0.1)  # 100ms para test rápido
        
        # Iniciar y fallar una carga
        assert breaker.start_loading() is True
        breaker.finish_loading(success=False)
        
        # Inmediatamente después del error, debe estar bloqueado
        assert breaker.can_execute() is False
        
        # Esperar el cooldown
        time.sleep(0.15)  # Esperar más que el cooldown
        
        # Después del cooldown, debe permitir ejecución
        assert breaker.can_execute() is True
    
    def test_circuit_breaker_reset_error_state(self):
        """Test que reset_error_state permite nuevas cargas inmediatas"""
        breaker = LoadingCircuitBreaker(cooldown=10.0)  # Cooldown largo
        
        # Causar un error
        breaker.start_loading()
        breaker.finish_loading(success=False)
        
        # Debe estar bloqueado por cooldown
        assert breaker.can_execute() is False
        
        # Reset del estado de error
        breaker.reset_error_state()
        
        # Ahora debe permitir ejecución inmediata
        assert breaker.can_execute() is True


class TestDebouncedEmitter:
    """Tests para el DebouncedEmitter"""
    
    def test_debounced_emitter_delays_signal(self, qtbot):
        """Test que el emisor debounced retrasa la señal"""
        emitter = DebouncedEmitter(delay_ms=100)
        signal_received = Mock()
        emitter.signal_emitted.connect(signal_received)
        
        # Emitir señal
        emitter.emit_debounced("title", "artist", "genre")
        
        # Inmediatamente no debe haber señal
        assert signal_received.call_count == 0
        
        # Esperar el delay
        qtbot.wait(150)
        
        # Ahora debe haber emitido la señal
        assert signal_received.call_count == 1
        signal_received.assert_called_with("title", "artist", "genre")
    
    def test_debounced_emitter_cancels_previous_signal(self, qtbot):
        """Test que emisiones rápidas cancelan las anteriores"""
        emitter = DebouncedEmitter(delay_ms=100)
        signal_received = Mock()
        emitter.signal_emitted.connect(signal_received)
        
        # Emitir múltiples señales rápidamente
        emitter.emit_debounced("title1", "artist1", "genre1")
        qtbot.wait(50)  # Esperar menos que el delay
        emitter.emit_debounced("title2", "artist2", "genre2")
        qtbot.wait(50)
        emitter.emit_debounced("title3", "artist3", "genre3")
        
        # Esperar el delay completo
        qtbot.wait(150)
        
        # Solo debe haber emitido la última señal
        assert signal_received.call_count == 1
        signal_received.assert_called_with("title3", "artist3", "genre3")


class TestDatabaseConnectionError:
    """Tests para el manejo de errores de base de datos"""
    
    def test_database_connection_raises_custom_exceptions(self):
        """Test que DatabaseConnection lanza excepciones personalizadas"""
        # Usar un path inválido para forzar error
        db = DatabaseConnection("/invalid/path/that/does/not/exist.db")
        
        with pytest.raises(DatabaseConnectionError):
            with db.get_connection() as conn:
                pass


class TestMainWindowRecursionPrevention:
    """Tests para prevenir recursión en MainWindow"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock de conexión de base de datos"""
        mock_db = Mock(spec=DatabaseConnection)
        return mock_db
    
    @pytest.fixture
    def main_window(self, qtbot, mock_db_connection):
        """Fixture para MainWindow con dependencias mockeadas"""
        with patch('src.ui.windows.main_window.MusicService') as mock_music_service, \
             patch('src.ui.windows.main_window.AudioService') as mock_audio_service:
            
            window = MainWindow(mock_db_connection)
            qtbot.addWidget(window)
            return window
    
    def test_load_songs_prevents_recursion(self, main_window, qtbot):
        """Test que load_songs_for_library_view previene recursión"""
        call_count = 0
        original_method = main_window.load_songs_for_library_view
        
        def counting_wrapper(page):
            nonlocal call_count
            call_count += 1
            if call_count > 3:  # Detectar recursión
                pytest.fail("Detectada recursión en load_songs_for_library_view")
            
            # Simular que siempre falla para probar la prevención de recursión
            raise DatabaseConnectionError("Simulated DB error")
        
        # Mockear el método
        main_window.load_songs_for_library_view = counting_wrapper
        
        # Intentar cargar múltiples veces rápidamente
        try:
            main_window.load_songs_for_library_view(1)
        except DatabaseConnectionError:
            pass
            
        try:
            main_window.load_songs_for_library_view(1)  # Debe ser bloqueado
        except DatabaseConnectionError:
            pass
            
        try:
            main_window.load_songs_for_library_view(1)  # Debe ser bloqueado
        except DatabaseConnectionError:
            pass
        
        # Solo debe haber sido llamado una vez debido al circuit breaker
        assert call_count == 1
    
    def test_error_cooldown_prevents_immediate_retry(self, main_window):
        """Test que el cooldown de errores previene reintentos inmediatos"""
        # Simular un error para activar cooldown
        main_window._loading_circuit_breaker.start_loading()
        main_window._loading_circuit_breaker.finish_loading(success=False)
        
        # Verificar que está en cooldown
        assert not main_window._loading_circuit_breaker.can_execute()
        
        # Reset manual del estado
        main_window.reset_loading_errors()
        
        # Ahora debe permitir ejecución
        assert main_window._loading_circuit_breaker.can_execute()


class TestLibraryViewDebouncing:
    """Tests para el debouncing en LibraryView"""
    
    @pytest.fixture
    def library_view(self, qtbot):
        """Fixture para LibraryView"""
        mock_audio_service = Mock()
        view = LibraryView(mock_audio_service)
        qtbot.addWidget(view)
        return view
    
    def test_search_debouncing_delays_signal(self, library_view, qtbot):
        """Test que el debouncing retrasa la señal de búsqueda"""
        signal_received = Mock()
        library_view.search_changed.connect(signal_received)
        
        # Simular cambio de texto rápido
        library_view.search_field.setText("test")
        library_view.on_search_changed()  # Trigger manual
        
        # Inmediatamente no debe haber señal
        assert signal_received.call_count == 0
        
        # Esperar el delay de debouncing
        qtbot.wait(350)  # 300ms + margen
        
        # Ahora debe haber emitido la señal
        assert signal_received.call_count == 1
    
    def test_rapid_search_changes_cancel_previous(self, library_view, qtbot):
        """Test que cambios rápidos cancelan búsquedas anteriores"""
        signal_received = Mock()
        library_view.search_changed.connect(signal_received)
        
        # Simular múltiples cambios rápidos
        library_view.search_field.setText("test1")
        library_view.on_search_changed()
        
        qtbot.wait(100)  # Menos que el delay
        
        library_view.search_field.setText("test2")
        library_view.on_search_changed()
        
        qtbot.wait(100)
        
        library_view.search_field.setText("test3")
        library_view.on_search_changed()
        
        # Esperar el delay completo
        qtbot.wait(350)
        
        # Solo debe haber emitido una señal (la última)
        assert signal_received.call_count == 1


class TestErrorHandler:
    """Tests para el manejador de errores centralizado"""
    
    def test_error_handler_logs_errors(self):
        """Test que ErrorHandler registra errores correctamente"""
        import logging
        logger = ErrorHandler.setup_logging("test_logger", logging.DEBUG)
        
        # Test de error de DB
        error = DatabaseConnectionError("Test DB error")
        message = ErrorHandler.handle_db_error(logger, error, "test context")
        
        assert "Error de conexión a la base de datos" in message
        
        # Test de error general
        error = Exception("Test general error")
        message = ErrorHandler.handle_general_error(logger, error, "test context")
        
        assert "Error inesperado" in message


# Configuración de pytest
if __name__ == "__main__":
    pytest.main([__file__])
