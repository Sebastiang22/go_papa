import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import mysql.connector
from mysql.connector import Error

from core.config import settings


class MySQLUserManager:
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
            "Conexión a MySQL establecida para gestión de usuarios. Base de datos: '%s'",
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
            print("MySQL Database connection successful for user management")
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
            # Crear tabla de usuarios
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                address VARCHAR(255),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                INDEX (user_id)
            )
            """)
            self.connection.commit()
            print("Users table created successfully")
        except Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
    
    async def create_user(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo usuario en la base de datos MySQL o actualiza uno existente.

        :param user: Diccionario que representa el usuario con los campos user_id, name y address.
        :return: El usuario creado o actualizado, o None en caso de error.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            # Verificar si el usuario ya existe
            existing_user = await self.get_user(user["user_id"])
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                now = datetime.now()
                
                if existing_user:
                    # Actualizar usuario existente
                    query = """
                    UPDATE users 
                    SET name = %s, address = %s, updated_at = %s 
                    WHERE user_id = %s
                    """
                    cursor.execute(query, (
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
                    cursor.execute(query, (
                        user["user_id"],
                        user.get("name", ""),
                        user.get("address", ""),
                        now,
                        now
                    ))
                
                self.connection.commit()
                
                # Recuperar el usuario insertado o actualizado
                return await self.get_user(user["user_id"])
            except Error as err:
                logging.exception("Error al crear/actualizar el usuario: %s", err)
                return None
            finally:
                cursor.close()
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
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                
                if user:
                    # Convertir datetime a string para serialización JSON
                    if isinstance(user.get("created_at"), datetime):
                        user["created_at"] = user["created_at"].isoformat()
                    if isinstance(user.get("updated_at"), datetime):
                        user["updated_at"] = user["updated_at"].isoformat()
                    
                    # Obtener las órdenes del usuario
                    user_orders = await self.get_user_orders(user_id)
                    user["orders"] = user_orders
                    
                    logging.info("Usuario y órdenes recuperados con id: %s", user_id)
                    return user
                elif auto_create:
                    logging.warning("Usuario no encontrado con id: %s, creando nuevo usuario", user_id)
                    # Si el usuario no existe y auto_create es True, lo creamos
                    now = datetime.now()
                    query = """
                    INSERT INTO users (user_id, name, address, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        user_id,
                        "",
                        "",
                        now,
                        now
                    ))
                    self.connection.commit()
                    
                    # Recuperar el usuario recién creado
                    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                    new_user = cursor.fetchone()
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
            finally:
                cursor.close()
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
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return None

            cursor = self.connection.cursor(dictionary=True)
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
                
                # Add updated_at timestamp
                update_fields.append("updated_at = %s")
                values.append(datetime.now())
                
                # Add user_id for WHERE clause
                values.append(user_id)
                
                # Log update attempt
                logging.info("Attempting to update user %s with fields: %s", user_id, ", ".join(update_log))
                
                # Construct and execute the dynamic query
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"
                cursor.execute(query, tuple(values))
                self.connection.commit()
                
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
                logging.exception("Error updating user %s: %s", user_id, err)
                return None
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error in update_user_by_id: %s", e)
            return None

    async def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
                if self.connection is None or not self.connection.is_connected():
                    logging.error("Failed to connect to MySQL database")
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            try:
                # Modified query to include created_at in the SELECT list
                cursor.execute("""
                    SELECT DISTINCT enum_order_table, MAX(created_at) as created_at
                    FROM orders 
                    WHERE user_id = %s 
                    GROUP BY enum_order_table
                    ORDER BY created_at DESC
                """, (user_id,))
                
                distinct_orders = cursor.fetchall()
                summarized_orders = []
                
                for order_group in distinct_orders:
                    enum_order_table = order_group['enum_order_table']
                    
                    cursor.execute("""
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
                    
                    order_summary = cursor.fetchone()
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
            finally:
                cursor.close()
        except Exception as e:
            logging.exception("Error general al recuperar las órdenes del usuario: %s", e)
            return []