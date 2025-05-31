"""
Aplicación principal
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QEventLoop
from src.ui import MainWindow

class Application:
    """Clase principal de la aplicación"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = None
        
    def run(self):
        """Iniciar la aplicación"""
        try:
            # Evitar herencia de estilos del sistema operativo
            self.app.setStyle("Fusion") 

            # Configurar aplicación
            self.app.setApplicationName("Almacena")
            self.app.setApplicationDisplayName("Almacena - Sistema de Gestión")
            self.app.setApplicationVersion("1.0.0")
            
            print("[Main] Iniciando aplicación...")
            
            # Crear y mostrar ventana principal
            self.window = MainWindow()
            
            print("[Main] Ventana principal creada")
            
            # Iniciar un timer para imprimir el estado
            debug_timer = QTimer()
            debug_timer.setInterval(1000)  # cada segundo
            debug_timer.timeout.connect(self.debug_print)
            debug_timer.start()
            
            print("[Main] Iniciando bucle de eventos...")
            # Ejecutar aplicación
            return self.app.exec()
            
        except Exception as e:
            print(f"[Main] Error iniciando aplicación: {e}")
            import traceback
            traceback.print_exc()
            return 1
            
    def debug_print(self):
        """Imprimir información de debug"""
        if self.window:
            print(f"[Debug] Ventana visible: {self.window.isVisible()}")
            print(f"[Debug] Ventana activa: {self.window.isActiveWindow()}")

def main():
    """Función principal"""
    app = Application()
    return app.run()

if __name__ == '__main__':
    sys.exit(main())
