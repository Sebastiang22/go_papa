import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import mysql.connector
from mysql.connector import Error

from core.config import settings
from core import utils
import pdb

class MySQLOrderManager:
    def __init__(self):
        """
        Inicializa la conexión a MySQL utilizando los parámetros de configuración
        definidos en la clase 'settings'.
        
        Se esperan los siguientes atributos en 'settings':
            - db_host: Host del servidor MySQL
            - db_user: Usuario de MySQL
            - db_password: Contraseña de MySQL
            - db_database: Nombre de la base de datos
        """
        self.connection = None
        self._connect()
        self._create_tables()
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
            # Crear tabla de pedidos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(255) PRIMARY KEY,
                enum_order_table VARCHAR(255) NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL,
                price FLOAT DEFAULT 0,
                details TEXT,
                state VARCHAR(50) DEFAULT 'pendiente',
                address VARCHAR(255) NOT NULL,
                user_name VARCHAR(255),
                user_id VARCHAR(255),
                restaurant_id VARCHAR(255) DEFAULT 'Macchiato',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                INDEX (enum_order_table),
                INDEX (address),
                INDEX (state),
                INDEX (created_at),
                INDEX (user_id)
            )
            """)
            self.connection.commit()
            print("Orders table created successfully")
        except Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
    
    async def create_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo pedido en la base de datos MySQL.

        :param order: Diccionario que representa el pedido.
        :return: El pedido creado o None en caso de error.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            # Asignar fecha de creación si no existe
            if "created_at" not in order:
                order["created_at"] = datetime.now().isoformat()
            
            # Convertir fechas ISO a objetos datetime para MySQL
            created_at = datetime.fromisoformat(order["created_at"].replace('Z', '+00:00'))
            updated_at = datetime.now()
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Preparar los campos y valores para la inserción
                fields = ["id", "enum_order_table", "product_id", "product_name", 
                          "quantity", "details", "state", "address", "user_name", "user_id",
                          "created_at", "updated_at"]
                
                # Agregar campos opcionales si existen
                if "price" in order:
                    fields.append("price")
                if "restaurant_id" in order:
                    fields.append("restaurant_id")
                
                # Crear placeholders para la consulta SQL
                placeholders = ", ".join(["%s"] * len(fields))
                fields_str = ", ".join(fields)
                
                # Preparar valores para la inserción
                values = []
                for field in fields:
                    if field == "created_at":
                        values.append(created_at)
                    elif field == "updated_at":
                        values.append(updated_at)
                    else:
                        values.append(order.get(field, None))
                
                # Ejecutar la inserción
                query = f"INSERT INTO orders ({fields_str}) VALUES ({placeholders})"
                cursor.execute(query, values)
                self.connection.commit()
                
                # Recuperar el pedido insertado
                cursor.execute("SELECT * FROM orders WHERE id = %s", (order["id"],))
                created_order = cursor.fetchone()
                
                logging.info("Pedido creado con id: %s", created_order.get("id"))
                return created_order
            except Error as err:
                logging.exception("Error al crear el pedido: %s", err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al crear el pedido: %s", e)
            return None
    
    async def get_order(self, order_id: str, partition_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Recupera un pedido a partir de su ID.

        :param order_id: ID del pedido.
        :param partition_key: Parámetro ignorado, incluido para compatibilidad con la versión CosmosDB.
        :return: El pedido encontrado o None si no existe o se produce algún error.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
                order = cursor.fetchone()
                
                if order:
                    logging.info("Pedido recuperado con id: %s", order_id)
                    return order
                else:
                    logging.warning("Pedido no encontrado con id: %s", order_id)
                    return None
            except Error as err:
                logging.exception("Error al recuperar el pedido %s: %s", order_id, err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar el pedido: %s", e)
            return None
    
    async def get_latest_order(self) -> Optional[Dict[str, Any]]:
        """
        Recupera el enum_order_table del último pedido registrado en la tabla.

        :param partition_key: Parámetro ignorado, mantenido por compatibilidad.
        :return: El enum_order_table del último pedido o None si no existe o se produce algún error.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT enum_order_table FROM orders ORDER BY created_at DESC LIMIT 1"
                )
                order = cursor.fetchone()
                
                if order:
                    logging.info("Último enum_order_table recuperado")
                    return order
                else:
                    logging.warning("No se encontraron pedidos en la tabla")
                    return None
            except Error as err:
                logging.exception("Error al recuperar el último enum_order_table: %s", err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar el último enum_order_table: %s", e)
            return None
    
    async def get_order_status_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Recupera el pedido consolidado (formateado) del último pedido para una dirección determinada,
        agrupando en el campo 'products' todos los productos que comparten el mismo 'enum_order_table'.

        Parámetros:
            address (str): Dirección de entrega del pedido.

        Retorna:
            Optional[Dict[str, Any]]: El pedido consolidado formateado con la siguiente estructura:
            {
                "id": <enum_order_table>,
                "address": <address>,
                "customer_name": <user_name>,
                "enum_order_table": <enum_order_table>,
                "products": [
                    {
                        "name": <product_name>,
                        "quantity": <quantity>,
                        "price": <price>
                    },
                    ...
                ],
                "created_at": <created_at>,
                "updated_at": <updated_at>,
                "state": <state>
            }
            o None en caso de no encontrarlo o producirse algún error.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Obtener el último pedido para la dirección
                cursor.execute(
                    "SELECT * FROM orders WHERE address = %s ORDER BY created_at DESC LIMIT 1", 
                    (address,)
                )
                latest_order = cursor.fetchone()
                
                if not latest_order:
                    logging.info("No se encontró ningún pedido para la dirección: %s", address)
                    return None
                
                enum_order_table = latest_order.get("enum_order_table")
                if not enum_order_table:
                    logging.info("El último pedido para la dirección %s no tiene 'enum_order_table'.", address)
                    return None
                
                # Consultar todos los pedidos que compartan el mismo 'enum_order_table'
                cursor.execute(
                    "SELECT * FROM orders WHERE enum_order_table = %s ORDER BY created_at ASC", 
                    (enum_order_table,)
                )
                orders_in_group = cursor.fetchall()
                
                if not orders_in_group:
                    logging.warning("No se encontraron pedidos con enum_order_table: %s", enum_order_table)
                    return None
                
                # Construir el pedido consolidado
                first_order = orders_in_group[0]
                last_order = orders_in_group[-1]
                print("first_order: ", first_order)
                consolidated_order = {
                    "id": enum_order_table,
                    "address": first_order["address"],
                    "customer_name": first_order.get("user_name", ""),
                    "enum_order_table": enum_order_table,
                    "products": [],
                    "created_at": first_order.get("created_at").isoformat() if isinstance(first_order.get("created_at"), datetime) else first_order.get("created_at"),
                    "updated_at": latest_order.get("updated_at").isoformat() if isinstance(latest_order.get("updated_at"), datetime) else latest_order.get("updated_at"),
                    "state": latest_order.get("state", "pendiente")
                }
                
                # Agregar productos al pedido consolidado
                for order in orders_in_group:
                    product = {
                        "name": order.get("product_name", ""),
                        "quantity": order.get("quantity", 0),
                        "price": order.get("price", 0.0),
                        "details": order.get("details", "")
                    }
                    consolidated_order["products"].append(product)
                
                return consolidated_order
            except Error as err:
                logging.exception("Error al recuperar el estado del pedido para dirección %s: %s", address, err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar el estado del pedido: %s", e)
            return None
    
    async def get_today_orders_not_paid(self) -> Dict[str, Any]:
        """
        Retorna todos los pedidos creados el día actual (UTC) cuyo estado sea distinto de 'pagado',
        agrupando en el campo 'products' todos los productos que comparten el mismo 'enum_order_table'.

        Retorna:
            Dict[str, Any]: Diccionario con estadísticas y lista de pedidos.
            {
                "stats": {
                    "total_orders": int,
                    "pending_orders": int,
                    "complete_orders": int,
                    "total_sales": float
                },
                "orders": [
                    {
                        "id": str,
                        "table_id": str,
                        "customer_name": str,
                        "products": [...],
                        "created_at": str,
                        "updated_at": str,
                        "state": str
                    },
                    ...
                ]
            }
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return {"stats": {"total_orders": 0, "pending_orders": 0, "complete_orders": 0, "total_sales": 0}, "orders": []}
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Obtener la fecha actual en formato UTC
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_end = datetime.combine(today, datetime.max.time())
                
                # Consultar todos los pedidos de hoy
                cursor.execute("""
                    SELECT DISTINCT enum_order_table 
                    FROM orders 
                    WHERE created_at BETWEEN %s AND %s 
                    AND state != 'pagado'
                """, (today_start, today_end))
                
                distinct_orders = cursor.fetchall()
                orders_list = []
                
                # Estadísticas
                total_orders = 0
                pending_orders = 0
                complete_orders = 0
                total_sales = 0.0
                
                # Procesar cada grupo de pedidos
                for order_group in distinct_orders:
                    enum_order_table = order_group['enum_order_table']
                    
                    # Obtener todos los pedidos del grupo
                    cursor.execute("""
                        SELECT * FROM orders 
                        WHERE enum_order_table = %s 
                        ORDER BY created_at ASC
                    """, (enum_order_table,))
                    
                    orders_in_group = cursor.fetchall()
                    if not orders_in_group:
                        continue
                    
                    # Construir el pedido consolidado
                    first_order = orders_in_group[0]
                    last_order = orders_in_group[-1]
                    
                    consolidated_order = {
                        "id": enum_order_table,
                        "table_id": first_order.get("address", ""),
                        "customer_name": first_order.get("user_name", ""),
                        "products": [],
                        "created_at": first_order["created_at"].isoformat() if isinstance(first_order["created_at"], datetime) else first_order["created_at"],
                        "updated_at": last_order["updated_at"].isoformat() if isinstance(last_order["updated_at"], datetime) else last_order["updated_at"],
                        "state": last_order.get("state", "pendiente")
                    }
                    
                    # Agregar productos al pedido consolidado
                    order_total = 0.0
                    for order in orders_in_group:
                        product_price = order.get("price", 0.0)
                        product_quantity = order.get("quantity", 0)
                        product_total = product_price * product_quantity
                        
                        product = {
                            "name": order.get("product_name", ""),
                            "quantity": product_quantity,
                            "price": product_price,
                            "observations": order.get("details", "")
                        }
                        consolidated_order["products"].append(product)
                        order_total += product_total
                    
                    # Actualizar estadísticas
                    total_orders += 1
                    if consolidated_order["state"] == "pendiente":
                        pending_orders += 1
                    elif consolidated_order["state"] == "completado":
                        complete_orders += 1
                        total_sales += order_total
                    
                    orders_list.append(consolidated_order)
                
                # Construir el resultado final
                result = {
                    "stats": {
                        "total_orders": total_orders,
                        "pending_orders": pending_orders,
                        "complete_orders": complete_orders,
                        "total_sales": total_sales
                    },
                    "orders": orders_list
                }
                
                return result
                
            except Error as err:
                logging.exception("Error al recuperar los pedidos del día: %s", err)
                return {"stats": {"total_orders": 0, "pending_orders": 0, "complete_orders": 0, "total_sales": 0}, "orders": []}
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar los pedidos del día: %s", e)
            return {"stats": {"total_orders": 0, "pending_orders": 0, "complete_orders": 0, "total_sales": 0}, "orders": []}
    
    async def update_order_status_by_user_id(self, user_id: str, new_state: str) -> Optional[List[Dict[str, Any]]]:
        """
        Updates the status of all orders for a specific user.

        Parameters:
            user_id (str): The ID of the user whose orders will be updated.
            new_state (str): The new state to set for the orders.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of the updated orders, or None if an error occurs.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Update only orders that are not in 'terminado' state
                update_query = """
                UPDATE orders 
                SET state = %s, updated_at = %s 
                WHERE user_id = %s AND state != 'terminado'
                """
                
                now = datetime.now()
                cursor.execute(update_query, (new_state, now, user_id))
                self.connection.commit()
                
                # Fetch the updated orders
                cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
                updated_orders = cursor.fetchall()
                
                if updated_orders:
                    # Convert datetime objects to ISO format strings
                    for order in updated_orders:
                        if isinstance(order.get("created_at"), datetime):
                            order["created_at"] = order["created_at"].isoformat()
                        if isinstance(order.get("updated_at"), datetime):
                            order["updated_at"] = order["updated_at"].isoformat()
                    
                    logging.info("Updated %d orders for user: %s", len(updated_orders), user_id)
                    return updated_orders
                else:
                    logging.warning("No orders found for user: %s", user_id)
                    return None
            except Error as err:
                logging.exception("Error updating orders for user %s: %s", user_id, err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("General error updating orders: %s", e)
            return None
    
    
    async def get_pending_orders_by_user_id(self, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Recupera el último pedido de un usuario específico.

        :param user_id: ID del usuario.
        :return: El último pedido del usuario o None si no existe.
        """
        try:
            if not user_id:
                return None

            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Get the latest order for the user
                query = """
                    SELECT * FROM orders 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """
                cursor.execute(query, (user_id,))
                order = cursor.fetchone()
                
                if order:
                    if 'created_at' in order:
                        order['created_at'] = order['created_at'].isoformat()
                    if 'updated_at' in order:
                        order['updated_at'] = order['updated_at'].isoformat()
                    return order
                
                return None
            except Error as err:
                logging.exception("Error al recuperar pedido: %s", err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar pedido: %s", e)
            return None
    
    async def get_all_orders(self) -> Dict[str, Any]:
        """
        Retorna todos los pedidos en la base de datos,
        agrupando en el campo 'products' todos los productos que comparten el mismo 'enum_order_table'.

        Retorna:
            Dict[str, Any]: Diccionario con los pedidos agrupados por enum_order_table.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return {}
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Consultar todos los enum_order_table distintos
                cursor.execute("SELECT DISTINCT enum_order_table FROM orders")
                
                distinct_orders = cursor.fetchall()
                result = {}
                
                # Procesar cada grupo de pedidos
                for order_group in distinct_orders:
                    enum_order_table = order_group['enum_order_table']
                    
                    # Obtener todos los pedidos del grupo
                    cursor.execute("""
                        SELECT * FROM orders 
                        WHERE enum_order_table = %s 
                        ORDER BY created_at ASC
                    """, (enum_order_table,))
                    
                    orders_in_group = cursor.fetchall()
                    if not orders_in_group:
                        continue
                    
                    # Construir el pedido consolidado
                    first_order = orders_in_group[0]
                    last_order = orders_in_group[-1]
                    
                    consolidated_order = {
                        "id": enum_order_table,
                        "address": first_order["address"],
                        "customer_name": first_order.get("user_name", ""),
                        "enum_order_table": enum_order_table,
                        "products": [],
                        "created_at": first_order["created_at"].isoformat() if isinstance(first_order["created_at"], datetime) else first_order["created_at"],
                        "updated_at": last_order["updated_at"].isoformat() if isinstance(last_order["updated_at"], datetime) else last_order["updated_at"],
                        "state": last_order.get("state", "pendiente")
                    }
                    
                    # Agregar productos al pedido consolidado
                    for order in orders_in_group:
                        product = {
                            "name": order.get("product_name", ""),
                            "quantity": order.get("quantity", 0),
                            "price": order.get("price", 0.0),
                            "details": order.get("details", "")
                        }
                        consolidated_order["products"].append(product)
                    
                    result[enum_order_table] = consolidated_order
                
                return result
                
            except Error as err:
                logging.exception("Error al recuperar todos los pedidos: %s", err)
                return {}
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar todos los pedidos: %s", e)
            return {}

    async def get_order_status_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna el estado de todos los pedidos de un usuario específico.

        :param user_id: ID del usuario.
        :return: El estado de todos los pedidos del usuario.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
                orders = cursor.fetchall()
                
                if orders:
                    for order in orders:
                        if 'created_at' in order:
                            order['created_at'] = order['created_at'].isoformat()
                        if 'updated_at' in order:
                            order['updated_at'] = order['updated_at'].isoformat()
                
                return orders
            except Error as err:
                logging.exception("Error al recuperar estado de pedidos: %s", err)
                return []
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar estado de pedidos: %s", e)
            return []

    async def update_order_status(self, enum_order_table: str, state: str, partition_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Actualiza el campo 'state' de todos los pedidos que comparten el mismo 'enum_order_table'
        y retorna el pedido consolidado con la siguiente estructura:
        {
            "id": <enum_order_table>,
            "table_id": <table_id>,
            "customer_name": <user_name>,
            "products": [
                {
                    "name": <product_name>,
                    "quantity": <quantity>,
                    "price": <price>,
                    "observations": <details>
                },
                ...
            ],
            "created_at": <created_at>,
            "updated_at": <updated_at>,
            "state": <state>
        }

        Parámetros:
            enum_order_table (str): Valor que identifica el grupo de pedidos a actualizar.
            state (str): Nuevo estado (por ejemplo, "pendiente", "completado", etc.).
            partition_key (Optional[str]): Parámetro ignorado, incluido para compatibilidad.

        Retorna:
            Optional[Dict[str, Any]]: El pedido consolidado actualizado o None en caso de error.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Verificar si existen pedidos con ese enum_order_table
                cursor.execute(
                    "SELECT COUNT(*) as count FROM orders WHERE enum_order_table = %s",
                    (enum_order_table,)
                )
                count = cursor.fetchone()["count"]
                if count == 0:
                    logging.warning("No se encontraron pedidos con enum_order_table: %s", enum_order_table)
                    return None
                
                # Actualizar el estado de todos los pedidos con el mismo enum_order_table
                now = datetime.now()
                cursor.execute(
                    "UPDATE orders SET state = %s, updated_at = %s WHERE enum_order_table = %s",
                    (state, now, enum_order_table)
                )
                self.connection.commit()
                
                # Obtener todos los pedidos actualizados
                cursor.execute(
                    "SELECT * FROM orders WHERE enum_order_table = %s ORDER BY created_at ASC",
                    (enum_order_table,)
                )
                orders_in_group = cursor.fetchall()
                
                if not orders_in_group:
                    logging.warning("No se pudieron recuperar los pedidos actualizados con enum_order_table: %s", enum_order_table)
                    return None
                
                # Construir el pedido consolidado
                first_order = orders_in_group[0]
                last_order = orders_in_group[-1]
                
                consolidated_order = {
                    "id": enum_order_table,
                    "table_id": first_order.get("address", ""),
                    "customer_name": first_order.get("user_name", ""),
                    "products": [],
                    "created_at": first_order["created_at"].isoformat() if isinstance(first_order["created_at"], datetime) else first_order["created_at"],
                    "updated_at": now.isoformat(),
                    "state": state
                }
                
                # Agregar productos al pedido consolidado
                order_total = 0.0
                for order in orders_in_group:
                    product_price = float(order.get("price", 0.0))
                    product_quantity = int(order.get("quantity", 0))
                    product_total = product_price * product_quantity
                    order_total += product_total
                    
                    product = {
                        "name": order.get("product_name", ""),
                        "quantity": product_quantity,
                        "price": product_price,
                        "observations": order.get("details", "")
                    }
                    consolidated_order["products"].append(product)
                
                if state == "completado":
                    logging.info(f"Pedido marcado como completado: {enum_order_table}, valor total: {order_total}")
                
                logging.info("Estado actualizado para pedidos con enum_order_table %s: %s", enum_order_table, state)
                return consolidated_order
                
            except Error as err:
                logging.exception("Error al actualizar el estado de los pedidos con enum_order_table %s: %s", enum_order_table, err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al actualizar el estado de los pedidos: %s", e)
            return None

