import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import aiomysql
from aiomysql import Error

from core.config import settings
from core.db_pool import DBConnectionPool


class MySQLInventoryManager:
    def __init__(self):
        """
        Inicializa el gestor de inventario MySQL.
        Usa el pool de conexiones compartido en lugar de crear uno propio.
        """
        self.db_pool = DBConnectionPool()
        logging.info(
            "Gestor de inventario MySQL inicializado. Base de datos: '%s'",
            settings.db_database
        )
    
    async def _create_tables(self):
        """Crea las tablas necesarias si no existen."""
        pool = await self.db_pool.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # Crear tabla de inventario
                    await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory (
                        id VARCHAR(255) PRIMARY KEY,
                        restaurant_id VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        quantity INT NOT NULL,
                        unit VARCHAR(50) NOT NULL,
                        price FLOAT,
                        last_updated DATETIME NOT NULL,
                        INDEX (restaurant_id)
                    )
                    """)
                    await conn.commit()
                    logging.info("Inventory table created successfully")
                except Error as err:
                    logging.error(f"Error creating tables: {err}")
    
    async def add_product(self, restaurant_id: str, name: str, quantity: int, unit: str, price: float = None, descripcion: str = "", tipo_producto: str = "menu") -> Optional[Dict[str, Any]]:
        """
        Agrega un nuevo producto al inventario.
        """
        try:
            pool = await self.db_pool.get_pool()
            
            product = {
                "id": f"p-{datetime.now().timestamp()}",
                "restaurant_id": restaurant_id,
                "name": name,
                "quantity": quantity,
                "unit": unit,
                "price": price,
                "descripcion": descripcion,
                "tipo_producto": tipo_producto,
                "last_updated": datetime.now()
            }
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        query = """INSERT INTO inventory 
                                (id, restaurant_id, name, quantity, unit, price, last_updated)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                        values = (
                            product["id"],
                            product["restaurant_id"],
                            product["name"],
                            product["quantity"],
                            product["unit"],
                            product["price"],
                            product["last_updated"]
                        )
                        
                        await cursor.execute(query, values)
                        await conn.commit()
                        
                        # Convert datetime to isoformat for consistency with the interface
                        product["last_updated"] = product["last_updated"].isoformat()
                        
                        logging.info("Producto '%s' agregado al inventario del restaurante %s", name, restaurant_id)
                        return product
                    except Error as err:
                        await conn.rollback()
                        logging.exception("Error al agregar producto: %s", err)
                        return None
        except Exception as e:
            logging.exception("Error general al agregar producto: %s", e)
            return None
    
    async def get_inventory(self, restaurant_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario de un restaurante.
        """
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        query = "SELECT * FROM inventory WHERE restaurant_id = %s"
                        await cursor.execute(query, (restaurant_id,))
                        products = await cursor.fetchall()
                        
                        # Convert datetime objects to isoformat strings
                        for product in products:
                            product["last_updated"] = product["last_updated"].isoformat()
                        
                        return products
                    except Error as err:
                        logging.exception("Error al obtener inventario: %s", err)
                        return []
        except Exception as e:
            logging.exception("Error general al obtener productos del inventario: %s", e)
            return []
    
    async def get_adiciones(self, restaurant_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene las adiciones del inventario (tipo adicion) para un restaurant_id dado.
        
        Parámetros:
            restaurant_id (str): ID del restaurante. Si es None, se obtienen todas las adiciones.
        
        Retorna:
            List[Dict[str, Any]]: Lista de adiciones del inventario.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                if restaurant_id:
                    query = """
                    SELECT * FROM inventory 
                    WHERE restaurant_id = %s AND tipo_producto = 'adicion'
                    ORDER BY name
                    """
                    cursor.execute(query, (restaurant_id,))
                else:
                    query = """
                    SELECT * FROM inventory 
                    WHERE tipo_producto = 'adicion'
                    ORDER BY restaurant_id, name
                    """
                    cursor.execute(query)
                
                adiciones = cursor.fetchall()
                
                # Format datetime to isoformat for consistent API
                for adicion in adiciones:
                    if "last_updated" in adicion and adicion["last_updated"]:
                        adicion["last_updated"] = adicion["last_updated"].isoformat()
                
                logging.info("Obtenidas %d adiciones del inventario", len(adiciones))
                return adiciones
            except Error as err:
                logging.exception("Error al obtener adiciones del inventario: %s", err)
                return []
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al obtener adiciones del inventario: %s", e)
            return []
    
    async def update_product(self, product_id: str, updated_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza la información de un producto en el inventario.
        """
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # First, get the current product
                        query = "SELECT * FROM inventory WHERE id = %s AND restaurant_id = %s"
                        await cursor.execute(query, (product_id, updated_fields["restaurant_id"]))
                        product = await cursor.fetchone()
                        
                        if not product:
                            logging.warning("Producto no encontrado: %s", product_id)
                            return None
                        
                        # Update the product with new fields
                        product.update(updated_fields)
                        product["last_updated"] = datetime.now()
                        
                        # Prepare the update query
                        fields = [f"{key} = %s" for key in updated_fields.keys()]
                        fields.append("last_updated = %s")
                        query = f"UPDATE inventory SET {', '.join(fields)} WHERE id = %s"
                        
                        # Prepare values for the query
                        values = list(updated_fields.values())
                        values.append(product["last_updated"])
                        values.append(product_id)
                        
                        await cursor.execute(query, values)
                        await conn.commit()
                        
                        # Get the updated product
                        query = "SELECT * FROM inventory WHERE id = %s"
                        await cursor.execute(query, (product_id,))
                        updated_product = await cursor.fetchone()
                        
                        if updated_product:
                            updated_product["last_updated"] = updated_product["last_updated"].isoformat()
                        
                        logging.info("Producto actualizado: %s", product_id)
                        return updated_product
                    except Error as err:
                        await conn.rollback()
                        logging.exception("Error al actualizar producto: %s", err)
                        return None
        except Exception as e:
            logging.exception("Error general al actualizar producto: %s", e)
            return None
    
    async def delete_product(self, product_id: str, restaurant_id: str) -> bool:
        """
        Elimina un producto del inventario.
        """
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    try:
                        query = "DELETE FROM inventory WHERE id = %s AND restaurant_id = %s"
                        await cursor.execute(query, (product_id, restaurant_id))
                        await conn.commit()
                        
                        deleted = cursor.rowcount > 0
                        if deleted:
                            logging.info("Producto eliminado: %s", product_id)
                        else:
                            logging.warning("Producto no encontrado para eliminar: %s", product_id)
                        
                        return deleted
                    except Error as err:
                        await conn.rollback()
                        logging.exception("Error al eliminar producto: %s", err)
                        return False
        except Exception as e:
            logging.exception("Error general al eliminar producto: %s", e)
            return False
    
    async def close(self):
        """Cierra el pool de conexiones."""
        if self.db_pool:
            await self.db_pool.close()