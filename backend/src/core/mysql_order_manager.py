import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import aiomysql
from aiomysql import Error

from core.config import settings
from core.db_pool import DBConnectionPool
from core.utils import current_colombian_time
import pdb

class MySQLOrderManager:
    def __init__(self):
        """
        Inicializa el gestor de pedidos MySQL.
        Usa el pool de conexiones compartido en lugar de crear uno propio.
        """
        self.db_pool = DBConnectionPool()
        logging.info(
            "Gestor de pedidos MySQL inicializado. Base de datos: '%s'",
            settings.db_database
        )
    
    async def create_tables(self):
        """Crea las tablas necesarias si no existen."""
        pool = await self.db_pool.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # Crear tabla de pedidos
                    await cursor.execute("""
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
                        restaurant_id VARCHAR(255) DEFAULT 'go_papa',
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        INDEX (enum_order_table),
                        INDEX (address),
                        INDEX (state),
                        INDEX (created_at),
                        INDEX (user_id)
                    )
                    """)
                    await conn.commit()
                    logging.info("Orders table created successfully")
                except Error as err:
                    logging.error(f"Error creating tables: {err}")
    
    async def create_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea una nueva orden en la base de datos."""
        try:
            # Asignar fecha de creación si no existe
            if "created_at" not in order:
                # Usar la hora de Colombia en lugar de datetime.now()
                order["created_at"] = current_colombian_time()
            
            # Convertir fechas ISO a objetos datetime para MySQL
            created_at = datetime.strptime(order["created_at"].replace('Z', '+00:00'), '%Y-%m-%d %H:%M:%S') if 'T' not in order["created_at"] else datetime.fromisoformat(order["created_at"].replace('Z', '+00:00'))
            # Usar la hora de Colombia en lugar de datetime.now()
            updated_at = datetime.strptime(current_colombian_time(), '%Y-%m-%d %H:%M:%S')
            
            pool = await self.db_pool.get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Preparar los campos y valores para la inserción
                        fields = ["enum_order_table", "product_id", "product_name", 
                                "quantity", "state", "address", "user_name", "user_id",
                                "created_at", "updated_at"]
                        
                        # Agregar campos opcionales si existen
                        if "price" in order:
                            fields.append("price")
                        if "restaurant_id" in order:
                            fields.append("restaurant_id")
                        if "observaciones" in order:
                            fields.append("observaciones")
                        if "adicion" in order:
                            fields.append("adicion")
                        
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
                        await cursor.execute(query, values)
                        await conn.commit()
                        
                        # Recuperar el ID auto-incrementado
                        order_id = cursor.lastrowid
                        
                        # Recuperar el pedido insertado
                        await cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
                        created_order = await cursor.fetchone()
                        
                        logging.info("Pedido creado con id: %s", created_order.get("id"))
                        return created_order
                    except Error as err:
                        await conn.rollback()
                        logging.exception("Error al crear el pedido: %s", err)
                        return None
        except Exception as e:
            logging.exception("Error general al crear orden: %s", e)
            return None
    
    async def get_order(self, order_id: str, partition_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Recupera un pedido a partir de su ID.

        :param order_id: ID del pedido.
        :param partition_key: Parámetro ignorado, incluido para compatibilidad con la versión CosmosDB.
        :return: El pedido encontrado o None si no existe o se produce algún error.
        """
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        await cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
                        order = await cursor.fetchone()
                        
                        if order:
                            logging.info("Pedido recuperado con id: %s", order_id)
                            return order
                        else:
                            logging.warning("Pedido no encontrado con id: %s", order_id)
                            return None
                    except Error as err:
                        logging.exception("Error al recuperar el pedido %s: %s", order_id, err)
                        return None
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
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        await cursor.execute(
                            "SELECT enum_order_table FROM orders ORDER BY created_at DESC LIMIT 1"
                        )
                        order = await cursor.fetchone()
                        
                        if order:
                            logging.info("Último enum_order_table recuperado")
                            return order
                        else:
                            logging.warning("No se encontraron pedidos en la tabla")
                            return None
                    except Error as err:
                        logging.exception("Error al recuperar el último enum_order_table: %s", err)
                        return None
        except Exception as e:
            logging.exception("Error general al recuperar el último enum_order_table: %s", e)
            return None
    
    async def get_order_status_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Forzar commit para asegurar datos actualizados
                        await conn.commit()
                        
                        # Obtener la fecha actual (solo la parte de la fecha, sin la hora)
                        today_str = utils.current_colombian_time().split()[0]  # Obtener solo la fecha (YYYY-MM-DD)
                        today = datetime.strptime(today_str, '%Y-%m-%d').date()
                        today_start = datetime.combine(today, datetime.min.time())
                        
                        # Obtener el último pedido para la dirección del día actual
                        await cursor.execute(
                            "SELECT * FROM orders WHERE address = %s AND created_at >= %s ORDER BY created_at DESC LIMIT 1", 
                            (address, today_start)
                        )
                        latest_order = await cursor.fetchone()
                        
                        if not latest_order:
                            logging.info("No se encontró ningún pedido para la dirección %s en el día actual", address)
                            return None
                        
                        enum_order_table = latest_order.get("enum_order_table")
                        if not enum_order_table:
                            logging.info("El último pedido para la dirección %s no tiene 'enum_order_table'.", address)
                            return None

                        # Consultar todos los pedidos que compartan el mismo 'enum_order_table'
                        # Asegurar que enum_order_table sea string
                        enum_order_table_str = str(enum_order_table)
                        logging.info(f"Buscando pedidos con enum_order_table: {enum_order_table_str} (tipo: {type(enum_order_table_str)})")
                        await cursor.execute(
                            "SELECT * FROM orders WHERE enum_order_table = %s ORDER BY created_at ASC", 
                            (enum_order_table_str,)
                        )
                        orders_in_group = await cursor.fetchall()
                        
                        if not orders_in_group:
                            logging.warning("No se encontraron pedidos con enum_order_table: %s", enum_order_table_str)
                            return None
                        
                        logging.info(f"Encontrados {len(orders_in_group)} pedidos para enum_order_table {enum_order_table_str}")
                        for order in orders_in_group:
                            logging.info(f"Producto encontrado: {order.get('product_name')} - {order.get('quantity')}")
                        # Construir el pedido consolidado
                        first_order = orders_in_group[0]
                        last_order = orders_in_group[-1]
                        
                        consolidated_order = {
                            "id": enum_order_table,
                            "address": first_order["address"],
                            "customer_name": first_order.get("user_name", ""),
                            "enum_order_table": enum_order_table,
                            "products": [],
                            "created_at": first_order.get("created_at").isoformat() if isinstance(first_order.get("created_at"), datetime) else first_order.get("created_at"),
                            "updated_at": latest_order.get("updated_at").isoformat() if isinstance(latest_order.get("updated_at"), datetime) else latest_order.get("updated_at"),
                            "state": latest_order.get("state")
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
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                try:
                    # Establecer nivel de aislamiento antes de iniciar la transacción
                    async with conn.cursor() as isolation_cursor:
                        await isolation_cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                    
                    # Iniciar transacción explícita después de configurar el nivel de aislamiento
                    await conn.begin()
                    
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        # Obtener la fecha actual en formato UTC
                        today = datetime.now().date()
                        today_start = datetime.combine(today, datetime.min.time())
                        today_end = datetime.combine(today, datetime.max.time())
                        
                        # Obtener todos los pedidos y procesarlos en memoria
                        await cursor.execute("""
                            SELECT * FROM orders 
                            WHERE created_at BETWEEN %s AND %s 
                            AND state != 'pagado'
                            ORDER BY enum_order_table, created_at ASC
                        """, (today_start, today_end))
                        
                        all_orders = await cursor.fetchall()
                        
                        # Commit la transacción explícitamente
                        await conn.commit()
                        
                        # Procesar los resultados en memoria para evitar más consultas
                        orders_by_group = {}
                        
                        # Agrupar pedidos por enum_order_table
                        for order in all_orders:
                            enum_order_table = order['enum_order_table']
                            if enum_order_table not in orders_by_group:
                                orders_by_group[enum_order_table] = []
                            orders_by_group[enum_order_table].append(order)
                        
                        # Estadísticas
                        total_orders = len(orders_by_group)
                        pending_orders = 0
                        complete_orders = 0
                        total_sales = 0.0
                        
                        # Construir la lista de pedidos consolidados
                        orders_list = []
                        
                        for enum_order_table, orders_in_group in orders_by_group.items():
                            if not orders_in_group:
                                continue
                            
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
                                    "observations": order.get("observaciones", order.get("details", "")),
                                    "adicion": order.get("adicion", "")
                                }
                                consolidated_order["products"].append(product)
                                order_total += product_total
                            
                            # Actualizar estadísticas
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
                    # Revertir la transacción en caso de error
                    await conn.rollback()
                    logging.exception("Error al recuperar los pedidos del día: %s", err)
                    return {"stats": {"total_orders": 0, "pending_orders": 0, "complete_orders": 0, "total_sales": 0}, "orders": []}
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
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Update only orders that are not in 'terminado' state
                        update_query = """
                        UPDATE orders 
                        SET state = %s, updated_at = %s 
                        WHERE user_id = %s AND state != 'terminado'
                        """
                        
                        now = datetime.now()
                        await cursor.execute(update_query, (new_state, now, user_id))
                        await conn.commit()
                        
                        # Fetch the updated orders
                        await cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
                        updated_orders = await cursor.fetchall()
                        
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
        except Exception as e:
            logging.exception("General error updating orders: %s", e)
            return None
    
    
    async def get_pending_orders_by_user_id(self, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Recupera el último pedido del último enum_order_table del día actual para un usuario específico.

        :param user_id: ID del usuario.
        :return: El último pedido del usuario del día actual o None si no existe.
        """
        try:
            if not user_id:
                return None

            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Obtener la fecha actual (solo la parte de la fecha, sin la hora)
                        today = datetime.now().date()
                        today_start = datetime.combine(today, datetime.min.time())
                        
                        # Get the latest order with the most recent enum_order_table
                        query = """
                            SELECT * FROM orders 
                            WHERE user_id = %s 
                            AND created_at >= %s
                            ORDER BY enum_order_table DESC, created_at DESC 
                            LIMIT 1
                        """
                        await cursor.execute(query, (user_id, today_start))
                        order = await cursor.fetchone()
                        
                        if order:
                            # Convert datetime objects to ISO format strings
                            if isinstance(order.get('created_at'), datetime):
                                order['created_at'] = order['created_at'].isoformat()
                            if isinstance(order.get('updated_at'), datetime):
                                order['updated_at'] = order['updated_at'].isoformat()
                            return order
                        
                        return None
                    except Error as err:
                        logging.exception("Error al recuperar pedido: %s", err)
                        return None
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
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Consultar todos los enum_order_table distintos
                        await cursor.execute("SELECT DISTINCT enum_order_table FROM orders")
                        
                        distinct_orders = await cursor.fetchall()
                        result = {}
                        
                        # Procesar cada grupo de pedidos
                        for order_group in distinct_orders:
                            enum_order_table = order_group['enum_order_table']
                            
                            # Obtener todos los pedidos del grupo
                            await cursor.execute("""
                                SELECT * FROM orders 
                                WHERE enum_order_table = %s 
                                ORDER BY created_at ASC
                            """, (enum_order_table,))
                            
                            orders_in_group = await cursor.fetchall()
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
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        await cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
                        orders = await cursor.fetchall()
                        
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
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Verificar si existen pedidos con ese enum_order_table
                        await cursor.execute(
                            "SELECT COUNT(*) as count FROM orders WHERE enum_order_table = %s",
                            (enum_order_table,)
                        )
                        result = await cursor.fetchone()
                        count = result["count"]
                        if count == 0:
                            logging.warning("No se encontraron pedidos con enum_order_table: %s", enum_order_table)
                            return None
                        
                        # Actualizar el estado de todos los pedidos con el mismo enum_order_table
                        now = datetime.now()
                        await cursor.execute(
                            "UPDATE orders SET state = %s, updated_at = %s WHERE enum_order_table = %s",
                            (state, now, enum_order_table)
                        )
                        await conn.commit()
                        
                        # Obtener todos los pedidos actualizados
                        await cursor.execute(
                            "SELECT * FROM orders WHERE enum_order_table = %s ORDER BY created_at ASC",
                            (enum_order_table,)
                        )
                        orders_in_group = await cursor.fetchall()
                        
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
        except Exception as e:
            logging.exception("Error general al actualizar el estado de los pedidos: %s", e)
            return None

    async def delete_order(self, enum_order_table: str, partition_key: Optional[str] = None) -> bool:
        """
        Elimina un pedido y todos sus productos asociados de la base de datos.

        Args:
            enum_order_table: Identificador único del pedido
            partition_key: Clave de partición (opcional)

        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario
        """
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    try:
                        # Verificar si el pedido existe
                        await cursor.execute("SELECT COUNT(*) FROM orders WHERE enum_order_table = %s", (enum_order_table,))
                        result = await cursor.fetchone()
                        count = result[0]
                        
                        if count == 0:
                            logging.warning(f"Intentando eliminar un pedido que no existe: {enum_order_table}")
                            return False
                        
                        # Eliminar todos los productos asociados a este pedido
                        await cursor.execute("DELETE FROM orders WHERE enum_order_table = %s", (enum_order_table,))
                        await conn.commit()
                        
                        deleted_rows = cursor.rowcount
                        logging.info(f"Pedido eliminado: {enum_order_table}, {deleted_rows} productos eliminados")
                        
                        return deleted_rows > 0
                        
                    except Error as err:
                        logging.exception(f"Error al eliminar el pedido {enum_order_table}: {err}")
                        await conn.rollback()
                        return False
        except Exception as e:
            logging.exception(f"Error general al eliminar el pedido: {e}")
            return False

    async def close(self):
        """Cierra el pool de conexiones."""
        if self.db_pool:
            await self.db_pool.close()
            await self.db_pool.wait_closed()
            logging.info("Pool de conexiones cerrado correctamente.")

