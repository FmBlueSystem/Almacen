"""
Vista base para la aplicación
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSize

class BaseView:
    """Clase base mixin para todas las vistas de la aplicación"""
    
    def get_minimum_size(self) -> QSize:
        """
        Obtener tamaño mínimo recomendado
        
        Returns:
            QSize: Tamaño mínimo (ancho, alto)
        """
        return QSize(800, 600)
    
    def get_preferred_size(self) -> QSize:
        """
        Obtener tamaño preferido
        
        Returns:
            QSize: Tamaño preferido (ancho, alto)
        """
        return QSize(1280, 720)
    
    def on_theme_changed(self, is_dark: bool):
        """
        Manejar cambio de tema
        
        Args:
            is_dark: True si el tema es oscuro
        """
        pass
    
    def on_scale_changed(self, scale_factor: float):
        """
        Manejar cambio de escala
        
        Args:
            scale_factor: Factor de escala (1.0 = sin escala)
        """
        pass
    
    def refresh(self):
        """Actualizar contenido de la vista"""
        pass
    
    def cleanup(self):
        """Limpiar recursos de la vista"""
        pass
