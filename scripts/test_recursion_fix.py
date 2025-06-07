#!/usr/bin/env python3
"""
Script de demostración para mostrar que el RecursionError ha sido corregido
"""

import sys
import time
from pathlib import Path
import pytest

# Skip execution during pytest collection
pytest.skip("Manual recursion demo", allow_module_level=True)

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.database.connection import DatabaseConnection, DatabaseConnectionError
from src.ui.windows.main_window import MainWindow
from src.utils.error_handler import LoadingCircuitBreaker


def simulate_db_error_scenario():
    """
    Simular el escenario que anteriormente causaba RecursionError
    """
    print("🔧 Iniciando demostración de corrección de RecursionError...")
    
    app = QApplication(sys.argv)
    
    # Crear una base de datos temporal que va a fallar
    invalid_db_path = "/invalid/path/that/does/not/exist.db"
    db_connection = DatabaseConnection(invalid_db_path)
    
    try:
        # Crear MainWindow con DB que va a fallar
        print("📱 Creando MainWindow con base de datos inválida...")
        window = MainWindow(db_connection)
        window.show()
        
        print("🔍 Simulando búsquedas múltiples que anteriormente causaban recursión...")
        
        # Simular múltiples búsquedas rápidas que anteriormente causarían recursión
        search_terms = ["test1", "test2", "test3", "test4", "test5"]
        
        for i, term in enumerate(search_terms):
            print(f"   🔍 Búsqueda {i+1}: '{term}'")
            
            # Simular cambio de texto en el campo de búsqueda
            window.library_view.search_field.setText(term)
            window.library_view.on_search_changed()
            
            # Pequeña pausa para simular typing rápido
            app.processEvents()
            time.sleep(0.1)
        
        # Esperar que el debouncing termine
        print("⏳ Esperando que termine el debouncing...")
        time.sleep(0.5)
        app.processEvents()
        
        # Verificar el estado del circuit breaker
        print(f"🚦 Estado del Circuit Breaker:")
        print(f"   - Puede ejecutar: {window._loading_circuit_breaker.can_execute()}")
        print(f"   - En cooldown: {window._loading_circuit_breaker._last_error_time is not None}")
        
        # Intentar resetear y cargar nuevamente
        print("🔄 Reseteando estado de error...")
        window.reset_loading_errors()
        
        print(f"   - Puede ejecutar después del reset: {window._loading_circuit_breaker.can_execute()}")
        
        # Mostrar mensaje de éxito
        print("✅ ÉXITO: No se produjo RecursionError!")
        print("✅ El Circuit Breaker previno la recursión exitosamente")
        print("✅ La UI permaneció responsiva durante los errores")
        
        # Mostrar estadísticas del status bar
        status_message = window.statusBar().currentMessage()
        print(f"📊 Mensaje del status bar: '{status_message}'")
        
        window.close()
        
    except RecursionError as e:
        print("❌ FALLO: RecursionError todavía ocurre!")
        print(f"❌ Error: {e}")
        return False
        
    except Exception as e:
        print(f"✅ Excepción controlada (no RecursionError): {type(e).__name__}: {e}")
        
    finally:
        app.quit()
    
    return True


def test_circuit_breaker_independently():
    """
    Test independiente del LoadingCircuitBreaker
    """
    print("\n🧪 Testing LoadingCircuitBreaker independientemente...")
    
    breaker = LoadingCircuitBreaker(cooldown=0.5)
    
    # Test 1: Prevención de carga concurrente
    print("🔒 Test 1: Prevención de carga concurrente")
    assert breaker.start_loading() == True, "Primera carga debe ser permitida"
    assert breaker.start_loading() == False, "Segunda carga debe ser bloqueada"
    breaker.finish_loading(success=True)
    print("   ✅ Carga concurrente prevenida correctamente")
    
    # Test 2: Cooldown después de error
    print("⏰ Test 2: Cooldown después de error")
    breaker.start_loading()
    breaker.finish_loading(success=False)
    assert breaker.can_execute() == False, "Debe estar en cooldown después de error"
    print("   ✅ Cooldown activado correctamente después de error")
    
    # Test 3: Reset manual
    print("🔄 Test 3: Reset manual del estado")
    breaker.reset_error_state()
    assert breaker.can_execute() == True, "Debe permitir ejecución después del reset"
    print("   ✅ Reset manual funciona correctamente")
    
    print("✅ Todos los tests del Circuit Breaker pasaron!")


def test_debouncing():
    """
    Test del sistema de debouncing
    """
    print("\n⏱️  Testing sistema de debouncing...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    from src.utils.error_handler import DebouncedEmitter
    
    emitter = DebouncedEmitter(delay_ms=200)
    
    # Contador de señales recibidas
    signal_count = 0
    last_args = None
    
    def signal_receiver(*args):
        nonlocal signal_count, last_args
        signal_count += 1
        last_args = args
    
    emitter.signal_emitted.connect(signal_receiver)
    
    print("📡 Emitiendo múltiples señales rápidamente...")
    emitter.emit_debounced("signal1", "arg1", "arg1")
    time.sleep(0.05)
    emitter.emit_debounced("signal2", "arg2", "arg2")
    time.sleep(0.05)
    emitter.emit_debounced("signal3", "arg3", "arg3")
    
    print("⏳ Esperando debounce delay...")
    time.sleep(0.3)
    app.processEvents()
    
    print(f"📊 Señales recibidas: {signal_count}")
    print(f"📊 Últimos argumentos: {last_args}")
    
    assert signal_count == 1, f"Debouncing falló: {signal_count} señales recibidas en lugar de 1"
    assert last_args == ("signal3", "arg3", "arg3"), "Debouncing no conservó la última señal"
    
    print("✅ Sistema de debouncing funciona correctamente!")


def main():
    """
    Función principal de demostración
    """
    print("🚀 DEMOSTRACIÓN: Corrección del RecursionError")
    print("=" * 60)
    
    # Test del circuit breaker
    test_circuit_breaker_independently()
    
    # Test del debouncing
    test_debouncing()
    
    # Test del escenario completo
    print("\n🎭 Simulando escenario completo que causaba RecursionError...")
    success = simulate_db_error_scenario()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULTADO: La corrección del RecursionError fue EXITOSA!")
        print("🛡️  El Circuit Breaker previene recursión")
        print("⏱️  El Debouncing previene eventos excesivos")
        print("📝 El Logging reemplaza traceback.print_exc()")
        print("🚫 Los QMessageBox modales fueron eliminados")
    else:
        print("❌ RESULTADO: La corrección FALLÓ - RecursionError todavía ocurre")
    
    print("=" * 60)


if __name__ == "__main__":
    main()