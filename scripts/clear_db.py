#!/usr/bin/env python3
"""
Script para limpiar todos los datos de la base de datos
"""

import sys
import logging
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.connection import DatabaseConnection

def setup_logging():
    """Configurar logging para el script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def clear_database(db_connection: DatabaseConnection):
    """Eliminar todos los datos de las tablas"""
    with db_connection.get_connection() as conn:
        cursor = conn.cursor()
        # Deshabilitar verificación de claves foráneas temporalmente
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            cursor.execute(f"DELETE FROM {table_name};")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
        
        # Reactivar verificación de claves foráneas
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

def main():
    """Función principal del script"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Solicitar confirmación
        response = input("¿Estás seguro de que deseas eliminar TODOS los datos? (escribe 'SI' para confirmar): ")
        if response.strip().upper() != "SI":
            logger.info("Operación cancelada por el usuario")
            return
        
        # Inicializar conexión a base de datos
        db_connection = DatabaseConnection()
        logger.info("Conexión a base de datos inicializada")
        
        # Limpiar base de datos
        clear_database(db_connection)
        logger.info("Base de datos limpiada exitosamente")
        
    except Exception as e:
        logger.error(f"Error limpiando base de datos: {e}")
        sys.exit(1)
    finally:
        pass  # La conexión se cierra automáticamente por el context manager

if __name__ == "__main__":
    main()