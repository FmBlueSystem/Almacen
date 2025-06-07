"""
Aplicación principal
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QEventLoop, QTranslator, QLocale, QLibraryInfo
from src.ui import MainWindow
from src.database.connection import DatabaseConnection
from src.database.migrations import MigrationManager

class Application:
    """Clase principal de la aplicación"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = None
        self.db_connection = None
        
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
            
            # Configurar traducciones
            locale = QLocale.system() # Obtener el locale del sistema
            print(f"[Main] Locale del sistema: {locale.name()}")

            # Traductor para Qt (botones estándar, etc.)
            qt_translator = QTranslator()
            qt_base_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            if qt_translator.load(locale, "qtbase", "_", qt_base_translations_path):
                self.app.installTranslator(qt_translator)
                print(f"[Main] Traductor Qt 'qtbase_{locale.name()}' cargado desde: {qt_base_translations_path}")
            else:
                print(f"[Main] No se pudo cargar el traductor Qt para {locale.name()} desde {qt_base_translations_path}")


            # Traductor para la aplicación
            app_translator = QTranslator()
            # Asumimos que las traducciones están en assets/translations/almacena_es.qm, por ejemplo.
            # Para una implementación real, podrías tener una lista de idiomas soportados y archivos.
            translation_path = "assets/translations" 
            # Intentar cargar el archivo específico del locale, ej. almacena_es_ES.qm o almacena_es.qm
            # Aquí simplificamos a un nombre fijo por ahora para el ejemplo:
            # Por ejemplo: if app_translator.load(locale, "almacena", "_", translation_path):
            # O un path más directo:
            target_qm_file = f"{translation_path}/almacena_{locale.name().split('_')[0]}.qm" # ej: almacena_es.qm
            if not app_translator.load(target_qm_file):
                 # Fallback a nombre de archivo más genérico si el específico no carga.
                 # Esto es solo un ejemplo, la lógica de carga puede ser más robusta.
                 print(f"[Main] No se pudo cargar {target_qm_file}, intentando forma genérica si existe.")
                 # if app_translator.load("almacena", translation_path):
                 #     print(f"[Main] Traductor de la aplicación 'almacena' (genérico) cargado desde {translation_path}.")
                 # else:
                 #     print(f"[Main] No se pudo cargar el traductor de la aplicación desde {translation_path}")
                 # Por ahora, solo intentamos cargar el archivo específico que podría existir.
                 print(f"[Main] El archivo de traducción {target_qm_file} no fue encontrado o no pudo ser cargado.")


            if app_translator.isEmpty():
                print(f"[Main] El traductor de la aplicación está vacío (no se cargaron cadenas). Buscado en: {target_qm_file}")
            else:
                self.app.installTranslator(app_translator)
                print(f"[Main] Traductor de la aplicación cargado: {target_qm_file}")

            # Inicializar conexión a la base de datos y ejecutar migraciones
            print("[Main] Configurando base de datos...")
            self.db_connection = DatabaseConnection() # Usa la ruta del .env por defecto
            migration_manager = MigrationManager(self.db_connection)
            migration_manager.run_migrations()
            print("[Main] Base de datos configurada y migraciones aplicadas.")
            
            # Crear y mostrar ventana principal, pasando la conexión
            self.window = MainWindow(db_connection=self.db_connection)
            
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
