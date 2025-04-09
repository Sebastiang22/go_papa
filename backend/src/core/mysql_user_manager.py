import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import aiomysql
from aiomysql import Error

from core.config import settings
from core.db_pool import DBConnectionPool
from core.utils import current_colombian_time

class MySQLUserManager:
    def __init__(self):
        """
        Inicializa el gestor de usuarios MySQL.
        Usa el pool de conexiones compartido en lugar de crear uno propio.
        """
        self.db_pool = DBConnectionPool()
        logging.info(
            "Gestor de usuarios MySQL inicializado. Base de datos: '%s'",
            settings.db_database
        )
    
    async def _create_tables(self):
        """Crea las tablas necesarias si no existen."""
        pool = await self.db_pool.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # Crear tabla de usuarios
                    await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255),
                        address VARCHAR(255),
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        INDEX (user_id)
                    )
                    """)
                    await conn.commit()
                    logging.info("Users table created successfully")
                except Error as err:
                    logging.error(f"Error creating tables: {err}")
    
    async def create_user(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo usuario en la base de datos MySQL o actualiza uno existente.

        :param user: Diccionario que representa el usuario con los campos user_id, name y address.
        :return: El usuario creado o actualizado, o None en caso de error.
        """
        try:
            # Verificar si el usuario ya existe
            existing_user = await self.get_user(user["user_id"])
            
            pool = await self.db_pool.get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        now = datetime.strptime(current_colombian_time(), '%Y-%m-%d %H:%M:%S')
                        
                        if existing_user:
                            # Actualizar usuario existente
                            query = """
                            UPDATE users 
                            SET name = %s, address = %s, updated_at = %s 
                            WHERE user_id = %s
                            """
                            await cursor.execute(query, (
                                user.get("name", existing_user.get("name")),
                                user.get("address", existing_user.get("address")),
                                now,
                                user["user_id"]
                            ))
                        else:
                            # Crear nuevo usuario
                            query = """
                            INSERT INTO users (user_id, name, address, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            await cursor.execute(query, (
                                user["user_id"],
                                user.get("name", ""),
                                user.get("address", ""),
                                now,
                                now
                            ))
                        
                        await conn.commit()
                        
                        # Recuperar el usuario insertado o actualizado
                        return await self.get_user(user["user_id"])
                    except Error as err:
                        await conn.rollback()
                        logging.exception("Error al crear/actualizar el usuario: %s", err)
                        return None
        except Exception as e:
            logging.exception("Error general al crear/actualizar el usuario: %s", e)
            return None
    
    async def get_user(self, user_id: str, auto_create: bool = True) -> Optional[Dict[str, Any]]:
        """
        Recupera un usuario a partir de su ID, incluyendo su historial de órdenes.

        :param user_id: ID del usuario.
        :param auto_create: Si es True y el usuario no existe, lo crea automáticamente.
        :return: El usuario encontrado con su historial de órdenes o None si no existe o se produce algún error.
        """
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                        user = await cursor.fetchone()
                        
                        if user:
                            # Convertir datetime a string para serialización JSON
                            if isinstance(user.get("created_at"), datetime):
                                user["created_at"] = user["created_at"].isoformat()
                            if isinstance(user.get("updated_at"), datetime):
                                user["updated_at"] = user["updated_at"].isoformat()
                            
                            logging.info("Usuario y órdenes recuperados con id: %s", user_id)
                            return user
                        elif auto_create:
                            logging.warning("Usuario no encontrado con id: %s, creando nuevo usuario", user_id)
                            # Si el usuario no existe y auto_create es True, lo creamos
                            now = datetime.strptime(current_colombian_time(), '%Y-%m-%d %H:%M:%S')
                            query = """
                            INSERT INTO users (user_id, name, address, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            await cursor.execute(query, (
                                user_id,
                                "",
                                "",
                                now,
                                now
                            ))
                            await conn.commit()
                            
                            # Recuperar el usuario recién creado
                            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                            new_user = await cursor.fetchone()
                            if new_user:
                                if isinstance(new_user.get("created_at"), datetime):
                                    new_user["created_at"] = new_user["created_at"].isoformat()
                                if isinstance(new_user.get("updated_at"), datetime):
                                    new_user["updated_at"] = new_user["updated_at"].isoformat()
                                new_user["orders"] = []  # Usuario nuevo, sin órdenes
                            return new_user
                        else:
                            return None
                    except Error as err:
                        logging.exception("Error al recuperar el usuario %s: %s", user_id, err)
                        return None
        except Exception as e:
            logging.exception("Error general al recuperar el usuario: %s", e)
            return None
    
    async def update_user_by_id(self, user_id: str, name: Optional[str] = None, address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Updates user information by user ID.

        Parameters:
            user_id (str): The unique identifier of the user.
            name (Optional[str]): The new name of the user.
            address (Optional[str]): The new delivery address of the user.

        Returns:
            Optional[Dict[str, Any]]: The updated user information or None if update fails.
        """
        try:
            pool = await self.db_pool.get_pool()

            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Build dynamic query based on provided fields
                        update_fields = []
                        values = []
                        update_log = []
                        
                        if name is not None:
                            update_fields.append("name = %s")
                            values.append(name)
                            update_log.append(f"name='{name}'")
                        
                        if address is not None:
                            update_fields.append("address = %s")
                            values.append(address)
                            update_log.append(f"address='{address}'")
                        
                        if not update_fields:
                            logging.info("No fields to update for user: %s", user_id)
                            return await self.get_user(user_id)
                        
                        # Always add updated_at
                        update_fields.append("updated_at = %s")
                        values.append(datetime.strptime(current_colombian_time(), '%Y-%m-%d %H:%M:%S'))
                        update_log.append(f"updated_at='{current_colombian_time()}'")
                        values.append(user_id)
                        
                        # Log update attempt
                        logging.info("Attempting to update user %s with fields: %s", user_id, ", ".join(update_log))
                        
                        # Construct and execute the dynamic query
                        query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"
                        await cursor.execute(query, tuple(values))
                        await conn.commit()
                        
                        if cursor.rowcount > 0:
                            updated_user = await self.get_user(user_id)
                            if updated_user:
                                logging.info("Successfully updated user %s. Updated fields: %s", user_id, ", ".join(update_log))
                                return updated_user
                            else:
                                logging.error("User %s was updated but could not be retrieved", user_id)
                                return None
                        else:
                            logging.warning("No rows affected when updating user %s. User might not exist.", user_id)
                            return None
                            
                    except Error as err:
                        await conn.rollback()
                        logging.exception("Error updating user %s: %s", user_id, err)
                        return None
        except Exception as e:
            logging.exception("Error in update_user_by_id: %s", e)
            return None

    async def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            pool = await self.db_pool.get_pool()
            
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    try:
                        # Query to get the latest enum_order_table for the user
                        await cursor.execute("""
                            SELECT enum_order_table, created_at
                            FROM orders 
                            WHERE user_id = %s
                            ORDER BY created_at DESC
                            LIMIT 1
                        """, (user_id,))
                        
                        distinct_orders = await cursor.fetchall()
                        print(distinct_orders)
                        summarized_orders = []
                        
                        for order_group in distinct_orders:
                            enum_order_table = order_group['enum_order_table']
                            
                            await cursor.execute("""
                                SELECT 
                                    enum_order_table,
                                    GROUP_CONCAT(CONCAT(product_name, ' (', quantity, ')')) as products,
                                    MAX(state) as state,
                                    MAX(created_at) as created_at,
                                    address
                                FROM orders 
                                WHERE user_id = %s AND enum_order_table = %s 
                                GROUP BY enum_order_table, address
                            """, (user_id, enum_order_table))
                            
                            order_summary = await cursor.fetchone()
                            if order_summary:
                                summarized_order = {
                                    "order_id": enum_order_table,
                                    "products": [
                                        product.strip() 
                                        for product in order_summary['products'].split(',')
                                    ],
                                    "state": order_summary['state'],
                                    "created_at": order_summary['created_at'].isoformat() if isinstance(order_summary['created_at'], datetime) else order_summary['created_at'],
                                    "address": order_summary['address']
                                }
                                summarized_orders.append(summarized_order)
                        
                        return summarized_orders
                        
                    except Error as err:
                        logging.exception("Error al recuperar las órdenes del usuario %s: %s", user_id, err)
                        return []
        except Exception as e:
            logging.exception("Error general al recuperar las órdenes del usuario: %s", e)
            return []

    async def close(self):
        """Cierra el pool de conexiones."""
        if self.db_pool:
            await self.db_pool.close()
            logging.info("Pool de conexiones cerrado correctamente.")
