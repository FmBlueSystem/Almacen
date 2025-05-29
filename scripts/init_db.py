#!/usr/bin/env python3
"""
Script para inicializar la base de datos
"""

import sys
import logging
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.connection import DatabaseConnection
from database.migrations import MigrationManager

def setup_logging():
    """Configurar logging para el script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Función principal del script"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Inicializar conexión a base de datos
        db_connection = DatabaseConnection()
        logger.info("Conexión a base de datos inicializada")
        
        # Ejecutar migraciones
        migration_manager = MigrationManager(db_connection)
        migration_manager.run_migrations()
        
        logger.info("Base de datos inicializada exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 