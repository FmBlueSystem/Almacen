"""
Módulo de conexión a base de datos SQLite
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Gestor de conexión a base de datos SQLite"""
    
    def __init__(self, db_path: str = "data/almacena.db"):
        """
        Inicializar conexión a base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    @contextmanager
    def get_connection(self):
        """
        Context manager para obtener conexión a la base de datos
        
        Yields:
            sqlite3.Connection: Conexión activa
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Acceso por nombre de columna
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Error de base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Ejecutar consulta SELECT
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            list: Resultados de la consulta
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert_update_delete(self, query: str, params: tuple = ()) -> int:
        """
        Ejecutar consulta INSERT, UPDATE o DELETE
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            int: Número de filas afectadas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount 