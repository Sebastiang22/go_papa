from fastapi import APIRouter, HTTPException, Body, Query
from typing import Optional, Dict, Any
import logging

# Import the MySQL order manager
from core.mysql_order_manager import MySQLOrderManager
from core.schema_http import RequestHTTPUpdateState

# Crear el router de órdenes con un prefijo y etiqueta
orders_router = APIRouter()

# Crear una única instancia de MySQLOrderManager para todo el módulo
order_manager = MySQLOrderManager()


@orders_router.get("/today", response_model=Dict[str, Any])
async def get_today_orders_not_paid():
    """
    Retorna todos los pedidos creados el día actual (UTC) cuyo estado sea distinto de 'pagado',
    agrupando en el campo 'products' todos los productos que comparten el mismo 'enum_order_table'.
    """
    # Utilizar la instancia global
    orders = await order_manager.get_today_orders_not_paid()
    if not orders:
        raise HTTPException(status_code=404, detail="No se encontraron pedidos para hoy.")
    return orders

@orders_router.get("/latest/{address}", response_model=Dict[str, Any])
async def get_latest_order_status(address: str):
    """
    Obtiene el estado del último pedido para una dirección específica.
    """
    # Utilizar la instancia global
    order = await order_manager.get_order_status_by_address(address)
    if not order:
        raise HTTPException(status_code=404, detail=f"No se encontró pedido para la dirección {address}.")
    return order

@orders_router.put("/update_state", response_model=Dict[str, Any])
async def update_order_state(request: RequestHTTPUpdateState):
    """
    Actualiza el estado de un pedido.
    
    Parámetros (en RequestHTTPUpdateState):
      - order_id: ID del pedido a actualizar.
      - state: Nuevo estado (por ejemplo, "pendiente", "completado", etc.).
      - partition_key: (Opcional) Clave de partición.
    """
    try:
        # Utilizar la instancia global
        updated_order = await order_manager.update_order_status(
            enum_order_table=request.order_id,
            state=request.state,
            partition_key=request.partition_key
        )

        if not updated_order:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el pedido {request.order_id} o no se pudo actualizar."
            )
        return updated_order
    except Exception as e:
        logging.exception("Error al actualizar el estado del pedido: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al actualizar el pedido: {str(e)}"
        )

@orders_router.delete("/{order_id}")
async def delete_order(order_id: str, partition_key: Optional[str] = None):
    """
    Elimina un pedido identificado por su ID.
    
    Parámetros:
      - order_id: ID del pedido.
      - partition_key: (Opcional) Clave de partición.
    """
    # Utilizar la instancia global
    success = await order_manager.delete_order(order_id, partition_key)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el pedido {order_id} o no se pudo eliminar."
        )
    return {"detail": "Pedido eliminado correctamente.", "id": order_id}

@orders_router.post("/create", response_model=Dict[str, Any])
async def create_order(order: Dict[str, Any] = Body(...)):
    """
    Crea un nuevo pedido en la base de datos.
    
    El cuerpo de la petición debe ser un diccionario que represente el pedido.
    Ejemplo de estructura:
    {
        "id": "100002",
        "enum_order_table": "100002",
        "product_id": "prod-01",
        "product_name": "Café Americano",
        "quantity": 3,
        "price": 0,
        "details": "Sin azúcar",
        "state": "pendiente",
        "address": "Calle Principal 123",
        "user_name": "Santiago",
        "user_id": "user123"
    }
    """
    # Utilizar la instancia global
    created_order = await order_manager.create_order(order)
    if created_order is None:
        raise HTTPException(status_code=500, detail="Error al crear el pedido.")
    return created_order


@orders_router.put("/update_state_by_user", response_model=Dict[str, Any])
async def update_order_state_by_user(user_id: str = Query(...), state: str = Query(...)):
    """
    Actualiza el estado de todos los pedidos de un usuario específico.
    
    Parámetros:
      - user_id: ID del usuario cuyos pedidos se actualizarán.
      - state: Nuevo estado (por ejemplo, "pendiente", "completado", etc.).
    """
    # Utilizar la instancia global
    updated_orders = await order_manager.update_order_status_by_user_id(user_id, state)
    if not updated_orders:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron pedidos para el usuario {user_id} o no se pudieron actualizar."
        )
    return {"orders": updated_orders}


@orders_router.get("/all", response_model=Dict[str, Any])
async def get_all_orders():
    """
    Retorna todos los pedidos en la base de datos,
    agrupando en el campo 'products' todos los productos que comparten el mismo 'enum_order_table'.
    """
    # Utilizar la instancia global
    orders = await order_manager.get_all_orders()
    if not orders:
        raise HTTPException(status_code=404, detail="No se encontraron pedidos.")
    return orders

