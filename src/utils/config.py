"""
Módulo de configuración usando variables de entorno
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Inicializar configuración
        
        Args:
            env_file: Ruta al archivo .env (opcional)
        """
        self._load_environment(env_file)
        self._validate_config()
    
    def _load_environment(self, env_file: Optional[str] = None):
        """Cargar variables de entorno desde archivo .env"""
        if env_file:
            env_path = Path(env_file)
        else:
            # Buscar .env en el directorio raíz del proyecto
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Variables de entorno cargadas desde {env_path}")
        else:
            logger.warning(f"Archivo .env no encontrado en {env_path}")
    
    def _validate_config(self):
        """Validar configuración requerida"""
        required_vars = ['DATABASE_PATH']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Variables de entorno faltantes: {missing_vars}")
    
    # Configuración de base de datos
    @property
    def database_path(self) -> str:
        """Ruta a la base de datos"""
        return os.getenv('DATABASE_PATH', 'data/almacena.db')
    
    @property
    def database_backup_path(self) -> str:
        """Ruta para backups de base de datos"""
        return os.getenv('DATABASE_BACKUP_PATH', 'data/backups/')
    
    # Configuración de logging
    @property
    def log_level(self) -> str:
        """Nivel de logging"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()
    
    @property
    def log_file(self) -> str:
        """Archivo de log"""
        return os.getenv('LOG_FILE', 'logs/almacena.log')
    
    # Configuración de interfaz
    @property
    def theme(self) -> str:
        """Tema de la interfaz"""
        return os.getenv('THEME', 'dark')
    
    @property
    def language(self) -> str:
        """Idioma de la interfaz"""
        return os.getenv('LANGUAGE', 'es')
    
    @property
    def window_width(self) -> int:
        """Ancho de ventana por defecto"""
        return int(os.getenv('WINDOW_WIDTH', '1200'))
    
    @property
    def window_height(self) -> int:
        """Alto de ventana por defecto"""
        return int(os.getenv('WINDOW_HEIGHT', '800'))
    
    # Configuración de desarrollo
    @property
    def debug(self) -> bool:
        """Modo debug activado"""
        return os.getenv('DEBUG', 'false').lower() == 'true'
    
    @property
    def enable_profiling(self) -> bool:
        """Profiling activado"""
        return os.getenv('ENABLE_PROFILING', 'false').lower() == 'true'
    
    # Configuración de seguridad
    @property
    def secret_key(self) -> str:
        """Clave secreta de la aplicación"""
        key = os.getenv('SECRET_KEY')
        if not key or key == 'your-secret-key-here':
            logger.warning("SECRET_KEY no configurada o usando valor por defecto")
        return key or 'default-secret-key'
    
    @property
    def encryption_key(self) -> str:
        """Clave de encriptación"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key or key == 'your-encryption-key-here':
            logger.warning("ENCRYPTION_KEY no configurada o usando valor por defecto")
        return key or 'default-encryption-key'
    
    def get(self, key: str, default: Optional[Union[str, int, bool]] = None) -> Optional[Union[str, int, bool]]:
        """
        Obtener valor de configuración personalizado
        
        Args:
            key: Nombre de la variable de entorno
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la variable o default
        """
        return os.getenv(key, default)
    
    def to_dict(self) -> dict:
        """
        Convertir configuración a diccionario
        
        Returns:
            dict: Configuración como diccionario
        """
        return {
            'database_path': self.database_path,
            'database_backup_path': self.database_backup_path,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'theme': self.theme,
            'language': self.language,
            'window_width': self.window_width,
            'window_height': self.window_height,
            'debug': self.debug,
            'enable_profiling': self.enable_profiling
        }

# Instancia global de configuración
config = Config() 
