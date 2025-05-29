"""
Modelo base para entidades de datos
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

class BaseModel(ABC):
    """Modelo base para todas las entidades"""
    
    def __init__(self, **kwargs):
        """
        Inicializar modelo base
        
        Args:
            **kwargs: Atributos del modelo
        """
        self.id: Optional[int] = kwargs.get('id')
        self.created_at: Optional[datetime] = kwargs.get('created_at')
        self.updated_at: Optional[datetime] = kwargs.get('updated_at')
        
        # Asignar atributos específicos del modelo
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir modelo a diccionario
        
        Returns:
            Dict[str, Any]: Representación en diccionario
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Crear instancia desde diccionario
        
        Args:
            data: Datos del modelo
            
        Returns:
            BaseModel: Instancia del modelo
        """
        pass
    
    def __repr__(self) -> str:
        """Representación string del modelo"""
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __eq__(self, other) -> bool:
        """Comparar modelos por ID"""
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id 