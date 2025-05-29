"""
Modelo para elementos del almacén
"""

from typing import Dict, Any, Optional
from .base import BaseModel

class Item(BaseModel):
    """Modelo para elementos del almacén"""
    
    def __init__(self, **kwargs):
        """
        Inicializar item
        
        Args:
            **kwargs: Atributos del item
        """
        # Atributos específicos del item
        self.nombre: str = kwargs.get('nombre', '')
        self.descripcion: str = kwargs.get('descripcion', '')
        self.categoria_id: Optional[int] = kwargs.get('categoria_id')
        self.precio: float = kwargs.get('precio', 0.0)
        self.stock: int = kwargs.get('stock', 0)
        self.activo: bool = kwargs.get('activo', True)
        
        # Llamar al constructor base
        super().__init__(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir item a diccionario
        
        Returns:
            Dict[str, Any]: Representación en diccionario
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria_id': self.categoria_id,
            'precio': self.precio,
            'stock': self.stock,
            'activo': self.activo,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """
        Crear item desde diccionario
        
        Args:
            data: Datos del item
            
        Returns:
            Item: Instancia del item
        """
        return cls(**data)
    
    def __str__(self) -> str:
        """Representación string del item"""
        return f"{self.nombre} (Stock: {self.stock})"
    
    @property
    def valor_total(self) -> float:
        """Calcular valor total del stock"""
        return self.precio * self.stock
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        """
        Verificar si el stock está bajo
        
        Args:
            threshold: Umbral de stock bajo
            
        Returns:
            bool: True si el stock está bajo
        """
        return self.stock <= threshold 