"""
Configuración de la interfaz de usuario
"""

from pathlib import Path
from typing import Tuple

from src.utils.config import config

class UIConfig:
    """Configuración de la interfaz tomada del módulo central Config"""

    # Implements Dart AI Task: Refactor UIConfig to use Config

    # Tema
    THEME = config.theme

    # Resolución base como cadena WIDTHxHEIGHT
    BASE_RESOLUTION = config.get('BASE_RESOLUTION', f"{config.window_width}x{config.window_height}")

    # Familia de fuente
    FONT_FAMILY = config.get('FONT_FAMILY', 'Segoe UI, Helvetica, Arial, sans-serif')
    
    # Rutas
    ICONS_PATH = Path('assets/icons')
    
    @classmethod
    def get_base_resolution(cls) -> Tuple[int, int]:
        """Obtener resolución base como tupla de enteros"""
        try:
            width, height = cls.BASE_RESOLUTION.split('x')
            return (int(width), int(height))
        except (ValueError, AttributeError):
            return (1920, 1080)  # Valores por defecto
            
    @classmethod
    def get_scale_factor(cls, current_width: int, current_height: int) -> float:
        """
        Calcular factor de escala según resolución actual
        
        Args:
            current_width: Ancho actual de la ventana
            current_height: Alto actual de la ventana
            
        Returns:
            float: Factor de escala (1.0 = sin escala)
        """
        base_width, base_height = cls.get_base_resolution()
        
        # Usar la dimensión más restrictiva
        width_scale = current_width / base_width
        height_scale = current_height / base_height
        
        return min(width_scale, height_scale)
        
    @classmethod
    def scale_size(cls, size: int, current_width: int, current_height: int) -> int:
        """
        Escalar un tamaño según la resolución actual
        
        Args:
            size: Tamaño base a escalar
            current_width: Ancho actual de la ventana
            current_height: Alto actual de la ventana
            
        Returns:
            int: Tamaño escalado
        """
        scale = cls.get_scale_factor(current_width, current_height)
        return int(size * scale)
        
    @classmethod
    def is_dark_theme(cls) -> bool:
        """Verificar si está activo el tema oscuro"""
        return cls.THEME.lower() == 'dark'

    @classmethod
    def set_dark_theme(cls, dark: bool):
        """Actualizar el tema en memoria"""
        cls.THEME = 'dark' if dark else 'light'
