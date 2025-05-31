"""
Configuración de la interfaz de usuario
"""

import os
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv

class UIConfig:
    """Configuración de la interfaz desde variables de entorno"""
    
    # Cargar .env
    load_dotenv()
    
    # Tema
    THEME = os.getenv('THEME', 'light')
    
    # Resolución base
    BASE_RESOLUTION = os.getenv('BASE_RESOLUTION', '1920x1080')
    
    # Familia de fuente
    FONT_FAMILY = os.getenv('FONT_FAMILY', 'Roboto')
    
    # Rutas
    FONT_PATH = Path('assets/fonts/Roboto-Regular.ttf')
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
