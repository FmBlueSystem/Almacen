#!/usr/bin/env python3
"""
Almacena - Punto de entrada principal
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.main_window import MainWindow
from utils.config import config

def setup_logging():
    """Configurar sistema de logging"""
    log_dir = Path(config.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler()
        ]
    )

def main():
    """Función principal de la aplicación"""
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Almacena")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Freddy Molina")
    
    logger.info("Iniciando Almacena v0.1.0")
    
    try:
        # Crear y mostrar ventana principal
        window = MainWindow()
        window.show()
        
        logger.info("Interfaz gráfica inicializada exitosamente")
        
        # Ejecutar loop de eventos
        return app.exec()
        
    except Exception as e:
        logger.error(f"Error crítico al iniciar aplicación: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 