"""
Sistema de migraciones para versionado de base de datos
"""

import logging
from typing import List, Dict
from .connection import DatabaseConnection

logger = logging.getLogger(__name__)

class MigrationManager:
    """Gestor de migraciones de base de datos"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializar gestor de migraciones
        
        Args:
            db_connection: Instancia de conexión a base de datos
        """
        self.db = db_connection
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Crear tabla de migraciones si no existe"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_insert_update_delete(create_table_sql)
    
    def get_applied_migrations(self) -> List[str]:
        """
        Obtener lista de migraciones aplicadas
        
        Returns:
            List[str]: Versiones de migraciones aplicadas
        """
        query = "SELECT version FROM migrations ORDER BY version"
        results = self.db.execute_query(query)
        return [row['version'] for row in results]
    
    def apply_migration(self, version: str, description: str, sql_commands: List[str]):
        """
        Aplicar una migración
        
        Args:
            version: Versión de la migración (ej: "001")
            description: Descripción de la migración
            sql_commands: Lista de comandos SQL a ejecutar
        """
        applied_migrations = self.get_applied_migrations()
        
        if version in applied_migrations:
            logger.info(f"Migración {version} ya aplicada")
            return
        
        try:
            # Ejecutar comandos de migración
            for sql_command in sql_commands:
                self.db.execute_insert_update_delete(sql_command)
            
            # Registrar migración aplicada
            insert_migration_sql = """
            INSERT INTO migrations (version, description) 
            VALUES (?, ?)
            """
            self.db.execute_insert_update_delete(
                insert_migration_sql, 
                (version, description)
            )
            
            logger.info(f"Migración {version} aplicada exitosamente: {description}")
            
        except Exception as e:
            logger.error(f"Error aplicando migración {version}: {e}")
            raise
    
    def get_migrations_to_apply(self) -> List[Dict]:
        """
        Obtener lista de migraciones pendientes
        
        Returns:
            List[Dict]: Migraciones pendientes con metadata
        """
        applied = set(self.get_applied_migrations())
        all_migrations = self._get_all_migrations()
        
        return [
            migration for migration in all_migrations 
            if migration['version'] not in applied
        ]
    
    def _get_all_migrations(self) -> List[Dict]:
        """
        Definir todas las migraciones disponibles
        
        Returns:
            List[Dict]: Lista de todas las migraciones
        """
        return [
            {
                'version': '001',
                'description': 'Crear tablas iniciales',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS configuracion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        clave TEXT UNIQUE NOT NULL,
                        valor TEXT NOT NULL,
                        descripcion TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_configuracion_clave ON configuracion(clave)
                    """
                ]
            },
            {
                'version': '002',
                'description': 'Crear tabla de canciones',
                'sql_commands': [
                    """
                    CREATE TABLE IF NOT EXISTS songs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        artist TEXT NOT NULL,
                        album TEXT NOT NULL,
                        genre TEXT NOT NULL,
                        bpm INTEGER,
                        file_path TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title)
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist)
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre)
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_songs_file_path ON songs(file_path)
                    """
                ]
            }
        ]
    
    def run_migrations(self):
        """Ejecutar todas las migraciones pendientes"""
        pending_migrations = self.get_migrations_to_apply()
        
        if not pending_migrations:
            logger.info("No hay migraciones pendientes")
            return
        
        for migration in pending_migrations:
            self.apply_migration(
                migration['version'],
                migration['description'],
                migration['sql_commands']
            )
        
        logger.info(f"Se aplicaron {len(pending_migrations)} migraciones")
