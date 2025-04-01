import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import mysql.connector
from mysql.connector import Error

from core.config import settings


class MySQLInventoryManager:
    def __init__(self):
        """
        Inicializa la conexión a MySQL utilizando los parámetros de configuración
        definidos en la clase 'settings'.
        """
        self.connection = None
        self._connect()
        #self._create_tables()
        logging.info(
            "Conexión a MySQL establecida. Base de datos: '%s'",
            settings.db_database
        )
    
    def _connect(self):
        """Establece conexión a la base de datos MySQL usando settings."""
        try:
            self.connection = mysql.connector.connect(
                host=settings.db_host,
                user=settings.db_user,
                password=settings.db_password,
                database=settings.db_database
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen."""
        if self.connection is None or not self.connection.is_connected():
            self._connect()
            if self.connection is None or not self.connection.is_connected():
                print("Failed to connect to MySQL database")
                return
        
        cursor = self.connection.cursor()
        try:
            # Crear tabla de inventario
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id VARCHAR(255) PRIMARY KEY,
                restaurant_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL,
                unit VARCHAR(50) NOT NULL,
                price FLOAT,
                descripcion TEXT,
                tipo_producto ENUM('menu', 'adicion') DEFAULT 'menu',
                last_updated DATETIME NOT NULL,
                INDEX (restaurant_id)
            )
            """)
            self.connection.commit()
            print("Inventory table created successfully")
        except Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
    
    async def add_product(self, restaurant_id: str, name: str, quantity: int, unit: str, price: float = None, descripcion: str = "", tipo_producto: str = "menu") -> Optional[Dict[str, Any]]:
        """
        Agrega un nuevo producto al inventario.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
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
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                query = """INSERT INTO inventory 
                         (id, restaurant_id, name, quantity, unit, price, descripcion, tipo_producto, last_updated)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (
                    product["id"],
                    product["restaurant_id"],
                    product["name"],
                    product["quantity"],
                    product["unit"],
                    product["price"],
                    product["descripcion"],
                    product["tipo_producto"],
                    product["last_updated"]
                )
                
                cursor.execute(query, values)
                self.connection.commit()
                
                # Convert datetime to isoformat for consistency with the interface
                product["last_updated"] = product["last_updated"].isoformat()
                
                logging.info("Producto '%s' agregado al inventario del restaurante %s", name, restaurant_id)
                return product
            except Error as err:
                logging.exception("Error al agregar producto: %s", err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al agregar producto: %s", e)
            return None
    
    async def get_inventory(self, restaurant_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario de un restaurante.
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
                    WHERE restaurant_id = %s AND tipo_producto = 'menu'
                    ORDER BY name
                    """
                    cursor.execute(query, (restaurant_id,))
                else:
                    query = """
                    SELECT * FROM inventory 
                    WHERE tipo_producto = 'menu'
                    ORDER BY restaurant_id, name
                    """
                    cursor.execute(query)
                
                products = cursor.fetchall()
                
                # Format datetime to isoformat for consistent API
                for product in products:
                    if "last_updated" in product and product["last_updated"]:
                        product["last_updated"] = product["last_updated"].isoformat()
                
                logging.info("Obtenidos %d productos del inventario", len(products))
                return products
            except Error as err:
                logging.exception("Error al obtener productos del inventario: %s", err)
                return []
            finally:
                cursor.close()
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
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # First, get the current product
                query = "SELECT * FROM inventory WHERE id = %s AND restaurant_id = %s"
                cursor.execute(query, (product_id, updated_fields["restaurant_id"]))
                product = cursor.fetchone()
                
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
                
                cursor.execute(query, values)
                self.connection.commit()
                
                # Get the updated product
                query = "SELECT * FROM inventory WHERE id = %s"
                cursor.execute(query, (product_id,))
                updated_product = cursor.fetchone()
                
                if updated_product:
                    updated_product["last_updated"] = updated_product["last_updated"].isoformat()
                
                logging.info("Producto actualizado: %s", product_id)
                return updated_product
            except Error as err:
                logging.exception("Error al actualizar producto: %s", err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al actualizar producto: %s", e)
            return None
    
    async def delete_product(self, product_id: str, restaurant_id: str) -> bool:
        """
        Elimina un producto del inventario.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return False
            
            cursor = self.connection.cursor()
            try:
                query = "DELETE FROM inventory WHERE id = %s AND restaurant_id = %s"
                cursor.execute(query, (product_id, restaurant_id))
                self.connection.commit()
                
                if cursor.rowcount > 0:
                    logging.info("Producto eliminado: %s", product_id)
                    return True
                else:
                    logging.warning("Producto no encontrado: %s", product_id)
                    return False
            except Error as err:
                logging.exception("Error al eliminar producto: %s", err)
                return False
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al eliminar producto: %s", e)
            return False