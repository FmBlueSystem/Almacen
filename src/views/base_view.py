"""
Vista base para separar lógica de presentación
"""

import logging
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

class BaseView(QWidget, ABC):
    """Vista base para componentes de interfaz"""
    
    # Señales comunes
    data_changed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    status_message = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        Inicializar vista base
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.init_ui()
        self.connect_signals()
    
    @abstractmethod
    def init_ui(self):
        """
        Inicializar interfaz de usuario
        Debe ser implementado por las vistas específicas
        """
        pass
    
    def connect_signals(self):
        """
        Conectar señales y slots
        Puede ser sobrescrito por vistas específicas
        """
        pass
    
    def show_error(self, message: str):
        """
        Mostrar mensaje de error
        
        Args:
            message: Mensaje de error
        """
        self.logger.error(message)
        self.error_occurred.emit(message)
    
    def show_status(self, message: str):
        """
        Mostrar mensaje de estado
        
        Args:
            message: Mensaje de estado
        """
        self.logger.info(message)
        self.status_message.emit(message)
    
    def refresh_data(self):
        """
        Refrescar datos de la vista
        Puede ser sobrescrito por vistas específicas
        """
        self.logger.debug("Refreshing view data")
        self.data_changed.emit()
    
    def validate_input(self) -> bool:
        """
        Validar entrada de datos
        Puede ser sobrescrito por vistas específicas
        
        Returns:
            bool: True si la entrada es válida
        """
        return True
    
    def clear_form(self):
        """
        Limpiar formulario
        Puede ser sobrescrito por vistas específicas
        """
        pass
    
    def load_data(self, data=None):
        """
        Cargar datos en la vista
        Puede ser sobrescrito por vistas específicas
        
        Args:
            data: Datos a cargar
        """
        pass
    
    def save_data(self):
        """
        Guardar datos desde la vista
        Puede ser sobrescrito por vistas específicas
        
        Returns:
            bool: True si se guardó correctamente
        """
        return True 