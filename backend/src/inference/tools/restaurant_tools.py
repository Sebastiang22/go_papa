import pdb
import json
import os
import logging
from typing import Any, Optional, List, Dict, cast

import nest_asyncio
nest_asyncio.apply()

from langchain_core.tools import tool
from core.mysql_order_manager import MySQLOrderManager
from core.config import settings
from core.utils import genereta_id, generate_order_id
from typing import List, Dict, Any
from core.mysql_inventory_manager import MySQLInventoryManager
from dotenv import load_dotenv
import os
load_dotenv(override=True)

async def get_menu_tool(restaurant_name: str = "go_papa") -> List[Dict[str, Any]]:
    """
    Obtiene el menú del restaurante desde MySQL.

    :param restaurant_name: Nombre del restaurante a consultar.
    :return: Lista de diccionarios con la información del menú.
    """
    print(f"\033[92m\nget_menu_tool activada \nrestaurant_name: {restaurant_name}\033[0m")
    
    inventory_manager = MySQLInventoryManager()
    menu_items = await inventory_manager.get_inventory(restaurant_name)
    return menu_items

async def confirm_order_tool(
    product_id: str,
    product_name: str,
    quantity: int,
    address: str,
    price: float,
    user_name: Optional[str],
    details: Optional[str],
    restaurant_id: str = "go_papa",
    user_id: Optional[str] = None
    ) -> Optional[str]:
    """
    Realiza un pedido de un producto y lo guarda en MySQL.

    Parámetros:
        product_id (str): Identificador del producto a pedir.
        product_name (str): Nombre del producto.
        quantity (int): Cantidad del producto.
        address (str): Dirección de entrega del pedido.
        price (float): Precio del producto.
        user_name (Optional[str]): Nombre del usuario que realiza el pedido.
        details (Optional[str]): Detalles adicionales del pedido.
        restaurant_id (str): Identificador del restaurante. Por defecto "go_papa".
        user_id (Optional[str]): Identificador del usuario que realiza el pedido.

    Retorna:
        Optional[str]: Mensaje de confirmación si el pedido se realiza con éxito, o None en caso de error.
    """
    order_id = genereta_id()
    # Crear una única instancia de MySQLOrderManager
    order_manager = MySQLOrderManager()
    # Obtener el último pedido usando address
    latest_order = await order_manager.get_latest_order()
    txt_response = ""
     # Verificar si el usuario tiene órdenes pendientes
    last_order_user = await order_manager.get_pending_orders_by_user_id(user_id)
    #verifica si hay ordenes 
    if latest_order:
        print(f"pendiente_orders: {last_order_user}")
        # Si el usuario tiene órdenes pendientes, verificar el estado de la última orden
        if last_order_user :
            last_order_state = last_order_user['state']
            # Si el estado es 'pendiente' o 'enpreparacion', usar el mismo enum_order_table
            if last_order_state in ['pendiente', 'en preparacion']:
                enum_order_table = int(last_order_user['enum_order_table'])
                logging.info("Usuario tiene órdenes en proceso. Usando enum_order_table: %s", enum_order_table)
                txt_response += "Usuario tiene órdenes en proceso. "
            else:
                # Si el estado es 'completado', incrementar el enum_order_table
                enum_order_table = int(latest_order['enum_order_table']) + 1
                logging.info("Último pedido completado. Incrementando enum_order_table a: %s", enum_order_table)
                txt_response += "Último pedido completado. "
        else:
            # Si no hay órdenes pendientes, incrementar el enum_order_table
            enum_order_table = int(latest_order['enum_order_table']) + 1
            logging.info("No hay órdenes pendientes. Incrementando enum_order_table a: %s", enum_order_table)
            txt_response += "No hay órdenes pendientes. "
    else:
        logging.info("No se encontró un pedido previo para la dirección: %s", address)
        txt_response += "No se encontró un pedido previo para la dirección. "
        enum_order_table = 1

    state = "pendiente"
    print(
        f"\033[92m\nconfirm_order_tool activada\n"
        f"id: {order_id}\n"
        f"enum_order_table: {enum_order_table}\n"
        f"product_id: {product_id}\n"
        f"address: {address}\n"
        f"product_name: {product_name}\n"
        f"quantity: {quantity}\n"
        f"price: {price}\n"
        f"user_name: {user_name}\n"
        f"state: {state}\n"
        f"restaurant_id: {restaurant_id}\n"
        f"user_id: {user_id}\n"
        f"details: {details}\033[0m"
    )
    order = {
        "id": order_id,
        "enum_order_table": enum_order_table,
        "product_id": product_id,
        "product_name": product_name,
        "quantity": quantity,
        "details": details,
        "price": price,
        "state": state,
        "address": address,
        "user_name": user_name,
        "restaurant_id": restaurant_id,
        "user_id": user_id
    }
    try:
        
        created_order = await order_manager.create_order(order)

        if created_order:
            txt_response = f"Pedido creado: {created_order}"
            logging.info(f"Pedido creado: {created_order}")
        # Update user information if user_id is provided
        print(user_id)
        if user_id:
            # Crear una tarea en segundo plano para actualizar la información del usuario
            async def update_user_background():
                try:
                    from core.mysql_user_manager import MySQLUserManager
                    user_manager = MySQLUserManager()
                    updated_user = await user_manager.update_user_by_id(str(user_id), name=user_name, address=address)
                    if updated_user:
                        logging.info("User information updated successfully: %s", updated_user)
                        print(f"respuesta_actualizacion{updated_user}")
                    else:
                        logging.warning("Failed to update user information for user_id: %s", user_id)
                except Exception as e:
                    logging.error(f"Error updating user information in background: {e}")

            # Crear la tarea sin esperar su finalización
            import asyncio
            asyncio.create_task(update_user_background())

        return txt_response

    except Exception as e:
        logging.exception("Error al confirmar el pedido: %s", e)
        return None

async def get_order_status_tool(address: str, restaurant_id: str = "go_papa") -> str:
    """
    Consulta el estado del pedido consolidado para una dirección determinada.
    
    Parámetros:
        address (str): Dirección de entrega del pedido.
        restaurant_id (str): Identificador del restaurante. Por defecto "go_papa".
    
    Retorna:
        str: Información formateada del pedido o un mensaje informativo si no se encuentra.
    """
    # Crear una única instancia de MySQLOrderManager
    order_manager = MySQLOrderManager()
    order_info = await order_manager.get_order_status_by_address(address)
    if order_info is None:
        return f"No se encontró información del pedido para la dirección {address}."
    print(
        f"\033[92m\nget_order_status_tool activada\n"
        f"address: {address}\n"
        f"restaurant_id: {restaurant_id}\n"
        f"order_info: {json.dumps(order_info, indent=4)}\033[0m"
    )
    return f"Pedido: {order_info}"

async def send_menu_pdf_tool(user_id: str) -> str:
    """
    Envía las imágenes del menú del restaurante al usuario.
    
    Parámetros:
        user_id (str): Identificador del usuario (número de teléfono) al que se enviarán las imágenes.
    
    Retorna:
        str: Mensaje de confirmación si el envío se realiza con éxito, o mensaje de error en caso contrario.
    """
    print(f"\033[92m\nsend_menu_pdf_tool activada\nuser_id: {user_id}\033[0m")
    
    try:
        import requests
        
        whatsapp_api_url = "http://localhost:3001/api/send-images"
        
        # Preparar los datos para la solicitud
        payload = {
            "phone": user_id  # Cambiado de "number" a "phone" para coincidir con la API
        }
        
        # Realizar la solicitud POST al servicio de WhatsApp
        response = requests.post(whatsapp_api_url, json=payload)
        
        # Verificar la respuesta
        if response.status_code == 200:
            return f"Las imágenes del menú han sido enviadas exitosamente al número {user_id}."
        else:
            error_msg = response.json().get("message", "Error desconocido")
            return f"No se pudo enviar el menú: {error_msg}"
    
    except Exception as e:
        logging.exception("Error al enviar las imágenes del menú: %s", e)
        return f"Error al enviar las imágenes del menú: {str(e)}"
