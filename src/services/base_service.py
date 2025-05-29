"""
Servicio base para lógica de negocio
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Servicio base para operaciones de datos"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializar servicio base
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """
        Nombre de la tabla asociada al servicio
        
        Returns:
            str: Nombre de la tabla
        """
        pass
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Obtener todos los registros
        
        Returns:
            List[Dict[str, Any]]: Lista de registros
        """
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY id"
            results = self.db.execute_query(query)
            self.logger.debug(f"Retrieved {len(results)} records from {self.table_name}")
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Error getting all records from {self.table_name}: {e}")
            raise
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener registro por ID
        
        Args:
            record_id: ID del registro
            
        Returns:
            Optional[Dict[str, Any]]: Registro encontrado o None
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = ?"
            results = self.db.execute_query(query, (record_id,))
            
            if results:
                record = dict(results[0])
                self.logger.debug(f"Retrieved record {record_id} from {self.table_name}")
                return record
            else:
                self.logger.info(f"Record {record_id} not found in {self.table_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting record {record_id} from {self.table_name}: {e}")
            raise
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Crear nuevo registro
        
        Args:
            data: Datos del registro
            
        Returns:
            int: ID del registro creado
        """
        try:
            # Filtrar campos válidos para la tabla
            filtered_data = self._filter_valid_fields(data)
            
            # Construir query de inserción
            fields = list(filtered_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            fields_str = ', '.join(fields)
            
            query = f"""
                INSERT INTO {self.table_name} ({fields_str}) 
                VALUES ({placeholders})
            """
            
            values = tuple(filtered_data.values())
            rows_affected = self.db.execute_insert_update_delete(query, values)
            
            if rows_affected > 0:
                # Obtener ID del registro creado
                new_id = self._get_last_insert_id()
                self.logger.info(f"Created record {new_id} in {self.table_name}")
                return new_id
            else:
                raise Exception("No rows affected during insert")
                
        except Exception as e:
            self.logger.error(f"Error creating record in {self.table_name}: {e}")
            raise
    
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualizar registro existente
        
        Args:
            record_id: ID del registro
            data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Filtrar campos válidos
            filtered_data = self._filter_valid_fields(data)
            
            if not filtered_data:
                self.logger.warning(f"No valid fields to update for record {record_id}")
                return False
            
            # Agregar timestamp de actualización
            filtered_data['updated_at'] = 'CURRENT_TIMESTAMP'
            
            # Construir query de actualización
            set_clause = ', '.join([f"{field} = ?" for field in filtered_data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
            
            values = tuple(list(filtered_data.values()) + [record_id])
            rows_affected = self.db.execute_insert_update_delete(query, values)
            
            if rows_affected > 0:
                self.logger.info(f"Updated record {record_id} in {self.table_name}")
                return True
            else:
                self.logger.warning(f"No record {record_id} found to update in {self.table_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating record {record_id} in {self.table_name}: {e}")
            raise
    
    def delete(self, record_id: int) -> bool:
        """
        Eliminar registro
        
        Args:
            record_id: ID del registro
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = ?"
            rows_affected = self.db.execute_insert_update_delete(query, (record_id,))
            
            if rows_affected > 0:
                self.logger.info(f"Deleted record {record_id} from {self.table_name}")
                return True
            else:
                self.logger.warning(f"No record {record_id} found to delete in {self.table_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting record {record_id} from {self.table_name}: {e}")
            raise
    
    def _filter_valid_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtrar campos válidos para la tabla
        
        Args:
            data: Datos originales
            
        Returns:
            Dict[str, Any]: Datos filtrados
        """
        # Por defecto, excluir campos de metadata
        excluded_fields = {'id', 'created_at', 'updated_at'}
        return {k: v for k, v in data.items() if k not in excluded_fields}
    
    def _get_last_insert_id(self) -> int:
        """
        Obtener ID del último registro insertado
        
        Returns:
            int: ID del último registro
        """
        query = "SELECT last_insert_rowid()"
        result = self.db.execute_query(query)
        return result[0][0] if result else 0 