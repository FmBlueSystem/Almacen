"""
Servicio para gestión de items del almacén
"""

from typing import List, Optional
from .base_service import BaseService
from models.item import Item
from database.connection import DatabaseConnection

class ItemService(BaseService):
    """Servicio para operaciones con items"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializar servicio de items
        
        Args:
            db_connection: Conexión a base de datos
        """
        super().__init__(db_connection)
    
    @property
    def table_name(self) -> str:
        """Nombre de la tabla de items"""
        return "items"
    
    def get_all_items(self) -> List[Item]:
        """
        Obtener todos los items como objetos Item
        
        Returns:
            List[Item]: Lista de items
        """
        raw_data = self.get_all()
        return [Item.from_dict(data) for data in raw_data]
    
    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """
        Obtener item por ID como objeto Item
        
        Args:
            item_id: ID del item
            
        Returns:
            Optional[Item]: Item encontrado o None
        """
        raw_data = self.get_by_id(item_id)
        return Item.from_dict(raw_data) if raw_data else None
    
    def create_item(self, item: Item) -> int:
        """
        Crear nuevo item
        
        Args:
            item: Objeto Item a crear
            
        Returns:
            int: ID del item creado
        """
        data = item.to_dict()
        return self.create(data)
    
    def update_item(self, item_id: int, item: Item) -> bool:
        """
        Actualizar item existente
        
        Args:
            item_id: ID del item
            item: Objeto Item con datos actualizados
            
        Returns:
            bool: True si se actualizó correctamente
        """
        data = item.to_dict()
        return self.update(item_id, data)
    
    def delete_item(self, item_id: int) -> bool:
        """
        Eliminar item
        
        Args:
            item_id: ID del item
            
        Returns:
            bool: True si se eliminó correctamente
        """
        return self.delete(item_id)
    
    def search_items(self, search_term: str) -> List[Item]:
        """
        Buscar items por nombre o descripción
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            List[Item]: Items encontrados
        """
        try:
            query = """
                SELECT * FROM items 
                WHERE nombre LIKE ? OR descripcion LIKE ?
                ORDER BY nombre
            """
            search_pattern = f"%{search_term}%"
            results = self.db.execute_query(query, (search_pattern, search_pattern))
            
            items = [Item.from_dict(dict(row)) for row in results]
            self.logger.info(f"Found {len(items)} items matching '{search_term}'")
            return items
            
        except Exception as e:
            self.logger.error(f"Error searching items: {e}")
            raise
    
    def get_low_stock_items(self, threshold: int = 10) -> List[Item]:
        """
        Obtener items con stock bajo
        
        Args:
            threshold: Umbral de stock bajo
            
        Returns:
            List[Item]: Items con stock bajo
        """
        try:
            query = """
                SELECT * FROM items 
                WHERE stock <= ? AND activo = 1
                ORDER BY stock ASC
            """
            results = self.db.execute_query(query, (threshold,))
            
            items = [Item.from_dict(dict(row)) for row in results]
            self.logger.info(f"Found {len(items)} items with low stock (≤{threshold})")
            return items
            
        except Exception as e:
            self.logger.error(f"Error getting low stock items: {e}")
            raise
    
    def get_items_by_category(self, category_id: int) -> List[Item]:
        """
        Obtener items por categoría
        
        Args:
            category_id: ID de la categoría
            
        Returns:
            List[Item]: Items de la categoría
        """
        try:
            query = """
                SELECT * FROM items 
                WHERE categoria_id = ? AND activo = 1
                ORDER BY nombre
            """
            results = self.db.execute_query(query, (category_id,))
            
            items = [Item.from_dict(dict(row)) for row in results]
            self.logger.info(f"Found {len(items)} items in category {category_id}")
            return items
            
        except Exception as e:
            self.logger.error(f"Error getting items by category: {e}")
            raise
    
    def update_stock(self, item_id: int, new_stock: int) -> bool:
        """
        Actualizar stock de un item
        
        Args:
            item_id: ID del item
            new_stock: Nuevo stock
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            query = """
                UPDATE items 
                SET stock = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """
            rows_affected = self.db.execute_insert_update_delete(query, (new_stock, item_id))
            
            if rows_affected > 0:
                self.logger.info(f"Updated stock for item {item_id} to {new_stock}")
                return True
            else:
                self.logger.warning(f"No item {item_id} found to update stock")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating stock for item {item_id}: {e}")
            raise 