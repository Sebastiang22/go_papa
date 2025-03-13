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
    user_name: Optional[str],
    details: Optional[str],
    restaurant_id: str = "Macchiato",
) -> Optional[str]:
    """
    Realiza un pedido de un producto y lo guarda en MySQL.

    Parámetros:
        product_id (str): Identificador del producto a pedir.
        product_name (str): Nombre del producto.
        quantity (int): Cantidad del producto.
        address (str): Dirección de entrega del pedido.
        user_name (Optional[str]): Nombre del usuario que realiza el pedido.
        details (Optional[str]): Detalles adicionales del pedido.
        restaurant_id (str): Identificador del restaurante. Por defecto "Macchiato".

    Retorna:
        Optional[str]: Mensaje de confirmación si el pedido se realiza con éxito, o None en caso de error.
    """
    order_id = genereta_id()  # Función que genera un ID único para el pedido.
    
    # Obtener el último pedido usando address
    latest_order = await order_manager.get_latest_order(address)
    
    if latest_order is not None:
        logging.info("Último pedido realizado: %s", latest_order)
        enum_order_table = generate_order_id(latest_order, threshold_minutes=60) 
    else:
        logging.info("No se encontró un pedido previo para la dirección: %s", address)
        enum_order_table = 100000

    state = "pendiente"
    print(
        f"\033[92m\nconfirm_order_tool activada\n"
        f"id: {order_id}\n"
        f"enum_order_table: {enum_order_table}\n"
        f"product_id: {product_id}\n"
        f"address: {address}\n"
        f"product_name: {product_name}\n"
        f"quantity: {quantity}\n"
        f"user_name: {user_name}\n"
        f"state: {state}\n"
        f"restaurant_id: {restaurant_id}\n"
        f"details: {details}\033[0m"
    )
    order = {
        "id": order_id,
        "enum_order_table": enum_order_table,
        "product_id": product_id,
        "product_name": product_name,
        "quantity": quantity,
        "details": details,
        "state": state,
        "address": address,
        "user_name": user_name,
        "restaurant_id": restaurant_id
    }

    try:
        created_order = await order_manager.create_order(order)
        if created_order is not None:
            # TODO: Implement inventory update in MySQL
            return "Pedido realizado con éxito"
        else:
            return "Error al realizar el pedido"
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
