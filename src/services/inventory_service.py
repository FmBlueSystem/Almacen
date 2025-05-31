"""
Servicio para gestión del inventario
"""

import logging
from typing import List, Optional, Dict, Any
from database.connection import DatabaseConnection
from models.inventory_item import InventoryItem
from .base_service import BaseService

logger = logging.getLogger(__name__)

class InventoryService(BaseService):
    """Servicio para gestión del inventario"""
    
    def __init__(self):
        super().__init__()
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Crear tabla de inventario si no existe"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0.0,
            location TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                conn.execute(create_sql)
                conn.commit()
            logger.info("Tabla inventory_items verificada/creada")
        except Exception as e:
            logger.error(f"Error creando tabla inventory_items: {e}")
            raise
    
    def get_all_items(self, filters: Optional[Dict[str, Any]] = None) -> List[InventoryItem]:
        """
        Obtener todos los elementos del inventario con filtros opcionales
        
        Args:
            filters: Diccionario con filtros (category, status, search)
            
        Returns:
            Lista de elementos del inventario
        """
        try:
            db = DatabaseConnection()
            
            # Query base
            query = "SELECT * FROM inventory_items WHERE 1=1"
            params = []
            
            # Aplicar filtros
            if filters:
                if filters.get('category'):
                    query += " AND category = ?"
                    params.append(filters['category'])
                
                if filters.get('status'):
                    query += " AND status = ?"
                    params.append(filters['status'])
                
                if filters.get('search'):
                    query += " AND (name LIKE ? OR description LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term])
                
                if filters.get('low_stock'):
                    query += " AND quantity < 10"
            
            query += " ORDER BY name"
            
            with db.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                items = []
                for row in rows:
                    item_data = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'category': row[3],
                        'quantity': row[4],
                        'price': row[5],
                        'location': row[6],
                        'status': row[7],
                        'created_at': row[8],
                        'updated_at': row[9]
                    }
                    items.append(InventoryItem.from_dict(item_data))
                
                logger.info(f"Obtenidos {len(items)} elementos del inventario")
                return items
                
        except Exception as e:
            logger.error(f"Error obteniendo elementos del inventario: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Obtener todas las categorías disponibles"""
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT DISTINCT category FROM inventory_items WHERE category IS NOT NULL ORDER BY category"
                )
                categories = [row[0] for row in cursor.fetchall()]
                return categories
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {e}")
            return []
    
    def get_locations(self) -> List[str]:
        """Obtener todas las ubicaciones disponibles"""
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT DISTINCT location FROM inventory_items WHERE location IS NOT NULL ORDER BY location"
                )
                locations = [row[0] for row in cursor.fetchall()]
                return locations
        except Exception as e:
            logger.error(f"Error obteniendo ubicaciones: {e}")
            return []
    
    def add_item(self, item: InventoryItem) -> bool:
        """Agregar nuevo elemento al inventario"""
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO inventory_items 
                    (name, description, category, quantity, price, location, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.name, item.description, item.category,
                    item.quantity, item.price, item.location, item.status
                ))
                conn.commit()
                item.id = cursor.lastrowid
                logger.info(f"Elemento agregado: {item.name} (ID: {item.id})")
                return True
        except Exception as e:
            logger.error(f"Error agregando elemento: {e}")
            return False
    
    def update_item(self, item: InventoryItem) -> bool:
        """Actualizar elemento del inventario"""
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                conn.execute("""
                    UPDATE inventory_items 
                    SET name=?, description=?, category=?, quantity=?, 
                        price=?, location=?, status=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (
                    item.name, item.description, item.category,
                    item.quantity, item.price, item.location, item.status, item.id
                ))
                conn.commit()
                logger.info(f"Elemento actualizado: {item.name} (ID: {item.id})")
                return True
        except Exception as e:
            logger.error(f"Error actualizando elemento: {e}")
            return False
    
    def delete_item(self, item_id: int) -> bool:
        """Eliminar elemento del inventario"""
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                conn.execute("DELETE FROM inventory_items WHERE id=?", (item_id,))
                conn.commit()
                logger.info(f"Elemento eliminado (ID: {item_id})")
                return True
        except Exception as e:
            logger.error(f"Error eliminando elemento: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del inventario"""
        try:
            db = DatabaseConnection()
            with db.get_connection() as conn:
                # Total de elementos
                total_items = conn.execute("SELECT COUNT(*) FROM inventory_items").fetchone()[0]
                
                # Total de categorías
                total_categories = conn.execute(
                    "SELECT COUNT(DISTINCT category) FROM inventory_items"
                ).fetchone()[0]
                
                # Elementos con poco stock
                low_stock_items = conn.execute(
                    "SELECT COUNT(*) FROM inventory_items WHERE quantity < 10"
                ).fetchone()[0]
                
                # Valor total del inventario
                total_value = conn.execute(
                    "SELECT SUM(quantity * price) FROM inventory_items"
                ).fetchone()[0] or 0
                
                return {
                    'total_items': total_items,
                    'total_categories': total_categories,
                    'low_stock_items': low_stock_items,
                    'total_value': round(total_value, 2)
                }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_items': 0,
                'total_categories': 0,
                'low_stock_items': 0,
                'total_value': 0.0
            }
    
    def seed_sample_data(self):
        """Agregar datos de ejemplo al inventario"""
        sample_items = [
            InventoryItem(name="Laptop HP", description="Laptop HP Pavilion 15", category="Electrónicos", quantity=5, price=899.99, location="Almacén A"),
            InventoryItem(name="Mouse Logitech", description="Mouse inalámbrico", category="Accesorios", quantity=25, location="Almacén B", price=29.99),
            InventoryItem(name="Teclado Mecánico", description="Teclado mecánico RGB", category="Accesorios", quantity=8, price=149.99, location="Almacén B"),
            InventoryItem(name="Monitor 24\"", description="Monitor LED 24 pulgadas", category="Electrónicos", quantity=12, price=199.99, location="Almacén A"),
            InventoryItem(name="Silla Ergonómica", description="Silla de oficina ergonómica", category="Mobiliario", quantity=3, price=299.99, location="Almacén C"),
            InventoryItem(name="Escritorio", description="Escritorio de madera", category="Mobiliario", quantity=7, price=399.99, location="Almacén C"),
            InventoryItem(name="Cable HDMI", description="Cable HDMI 2m", category="Cables", quantity=50, price=15.99, location="Almacén B"),
            InventoryItem(name="Impresora", description="Impresora láser monocromática", category="Electrónicos", quantity=2, price=179.99, location="Almacén A"),
        ]
        
        for item in sample_items:
            self.add_item(item)
        
        logger.info(f"Agregados {len(sample_items)} elementos de ejemplo") 