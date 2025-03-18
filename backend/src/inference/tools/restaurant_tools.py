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

# Crear una única instancia de MySQLOrderManager
order_manager = MySQLOrderManager()

async def get_menu_tool(restaurant_name: str = "Macchiato") -> List[Dict[str, Any]]:
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
    restaurant_id: str = "Macchiato",
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
        restaurant_id (str): Identificador del restaurante. Por defecto "Macchiato".
        user_id (Optional[str]): Identificador del usuario que realiza el pedido.

    Retorna:
        Optional[str]: Mensaje de confirmación si el pedido se realiza con éxito, o None en caso de error.
    """
    order_id = genereta_id()

    # Obtener el último pedido usando address
    latest_order = await order_manager.get_latest_order()
    print()  
     # Verificar si el usuario tiene órdenes pendientes
    last_order_user = await order_manager.get_pending_orders_by_user_id(user_id)
    #verifica si hay ordenes 
    if latest_order:
        print(f"pendiente_orders: {last_order_user}")
        # Si el usuario tiene órdenes pendientes, verificar el estado de la última orden
        if last_order_user :
            last_order_state = last_order_user['state']
            # Si el estado es 'pendiente' o 'enpreparacion', usar el mismo enum_order_table
            if last_order_state in ['pendiente', 'enpreparacion']:
                enum_order_table = int(last_order_user['enum_order_table'])
                logging.info("Usuario tiene órdenes en proceso. Usando enum_order_table: %s", enum_order_table)
            else:
                # Si el estado es 'terminado', incrementar el enum_order_table
                enum_order_table = int(latest_order['enum_order_table']) + 1
                logging.info("Último pedido terminado. Incrementando enum_order_table a: %s", enum_order_table)
        else:
            # Si no hay órdenes pendientes, incrementar el enum_order_table
            enum_order_table = int(latest_order['enum_order_table']) + 1
            logging.info("No hay órdenes pendientes. Incrementando enum_order_table a: %s", enum_order_table)
    else:
        logging.info("No se encontró un pedido previo para la dirección: %s", address)
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

        logging.info(f"Pedido creado: {created_order}")
        # Update user information if user_id is provided
        print(user_id)
        if user_id:
            from core.mysql_user_manager import MySQLUserManager
            user_manager = MySQLUserManager()
            updated_user = await user_manager.update_user_by_id(str(user_id), name=user_name, address=address)
            if updated_user:
                logging.info("User information updated successfully: %s", updated_user)
                print(f"respuesta_actualizacion{updated_user}")
            else:
                logging.warning("Failed to update user information for user_id: %s", user_id)

        return "Pedido realizado con éxito"

    except Exception as e:
        logging.exception("Error al confirmar el pedido: %s", e)
        return None

async def get_order_status_tool(address: str, restaurant_id: str = "Macchiato") -> str:
    """
    Consulta el estado del pedido consolidado para una dirección determinada.
    
    Parámetros:
        address (str): Dirección de entrega del pedido.
        restaurant_id (str): Identificador del restaurante. Por defecto "Macchiato".
    
    Retorna:
        str: Información formateada del pedido o un mensaje informativo si no se encuentra.
    """
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

async def send_menu_pdf_tool(
    address: str,
    user_name: Optional[str],
    user_id: str,
    restaurant_id: str = "Macchiato"
) -> str:
    """
    Envía el PDF del menú al usuario a través de WhatsApp.

    Args:
        user_id ([str]): Identificador del usuario que realiza el pedido.
        restaurant_id (str): ID del restaurante. Por defecto "Macchiato".

    Returns:
        str: Mensaje de confirmación si el envío fue exitoso.
    """
    try:
        from cliente_whatsapp import ClienteWhatsApp
        cliente = ClienteWhatsApp()
        await cliente.conectar()
        
        if await cliente.enviar_pdf(user_id):
            return "El menú en PDF ha sido enviado exitosamente a tu WhatsApp. 📄✨"
        else:
            return "Lo siento, hubo un problema al enviar el menú en PDF. Por favor, intenta nuevamente más tarde. 😔"
    except Exception as e:
        logging.exception("Error al enviar el PDF del menú: %s", e)
        return "Lo siento, ocurrió un error al intentar enviar el menú en PDF. 😔"
