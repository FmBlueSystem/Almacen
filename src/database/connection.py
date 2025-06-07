"""
Módulo de conexión a base de datos SQLite
"""

import sqlite3
import logging
import time
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Error de conexión a la base de datos"""
    pass


class DatabaseTimeoutError(DatabaseConnectionError):
    """Timeout al conectar a la base de datos"""
    pass

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
        self._local = threading.local()
        self._local.connection = None
        
    @contextmanager
    def get_connection(self):
        """
        Context manager para obtener conexión a la base de datos.
        Reutiliza la conexión si ya existe una en el mismo hilo.
        
        Yields:
            sqlite3.Connection: Conexión activa
            
        Raises:
            DatabaseConnectionError: Error al conectar a la base de datos
            DatabaseTimeoutError: Timeout al conectar a la base de datos
        """
        # Si ya hay una conexión activa en este hilo, la reutilizamos
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            yield self._local.connection
            return

        conn = None
        try:
            # Conectar con timeout explícito
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.row_factory = sqlite3.Row  # Acceso por nombre de columna
            self._local.connection = conn
            yield conn
        except sqlite3.OperationalError as e:
            if conn:
                conn.rollback()
            if "database is locked" in str(e).lower():
                logger.error(f"Database timeout/lock error: {e}")
                raise DatabaseTimeoutError(f"La base de datos está bloqueada o no responde: {e}") from e
            else:
                logger.error(f"Database operational error: {e}")
                raise DatabaseConnectionError(f"Error operacional de base de datos: {e}") from e
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"General database error: {e}")
            raise DatabaseConnectionError(f"Error de base de datos: {e}") from e
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error connecting to database: {e}")
            raise DatabaseConnectionError(f"Error inesperado al conectar a la base de datos: {e}") from e
        finally:
            if conn:
                try:
                    conn.commit()  # Commit any pending transactions
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing database connection: {e}")
                self._local.connection = None
    
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
            return cursor.rowcount
