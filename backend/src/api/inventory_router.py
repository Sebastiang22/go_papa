from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List,Literal
import logging
from datetime import datetime
from core.schema_http import Product, AddProductRequest, UpdateProductRequest, DeleteProductRequest
# Import the MySQL inventory manager
from core.mysql_inventory_manager import MySQLInventoryManager

# Instancia del administrador de inventario - ya está correctamente como una instancia global
inventory_manager = MySQLInventoryManager()

# Definición de modelos Pydantic para las solicitudes y respuestas

# Definición del router
inventory_router = APIRouter()


@inventory_router.post("/add_product", response_model=Product)
async def add_product(request: AddProductRequest):
    """
    Ruta para agregar un nuevo producto al inventario.
    """
    try:
        product = await inventory_manager.add_product(
            restaurant_id=request.restaurant_id,
            name=request.name,
            quantity=request.quantity,
            unit=request.unit,
            price=request.price
        )
        return product
    except Exception as e:
        logging.error("Error agregando producto: %s", str(e))
        raise HTTPException(status_code=500, detail="Error agregando producto al inventario")


@inventory_router.get("/inventory", response_model=List[Product])
async def get_inventory(restaurant_id: Literal["go_papa"] = None):
    """
    Ruta para obtener el inventario de un restaurante.
    Se debe pasar el restaurant_id como query parameter.
    """
    try:

        products = await inventory_manager.get_inventory(restaurant_id)
        if not products:
            raise HTTPException(status_code=404, detail="No se encontraron productos en el inventario")
        return products
    except Exception as e:
        logging.error("Error obteniendo inventario: %s", str(e))
        raise HTTPException(status_code=500, detail="Error obteniendo inventario")


@inventory_router.put("/update_product", response_model=Product)
async def update_product(request: UpdateProductRequest):
    """
    Ruta para actualizar la información de un producto en el inventario.
    Se actualizan solo los campos enviados en la solicitud.
    """
    # Se arma un diccionario con los campos a actualizar.
    updated_fields = {"restaurant_id": request.restaurant_id}
    if request.name is not None:
        updated_fields["name"] = request.name
    if request.quantity is not None:
        updated_fields["quantity"] = request.quantity
    if request.unit is not None:
        updated_fields["unit"] = request.unit
    if request.price is not None:
        updated_fields["price"] = request.price

    try:
        updated_product = await inventory_manager.update_product(request.product_id, updated_fields)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return updated_product
    except Exception as e:
        logging.error("Error actualizando producto: %s", str(e))
        raise HTTPException(status_code=500, detail="Error actualizando producto")


@inventory_router.delete("/delete_product", response_model=dict)
async def delete_product(request: DeleteProductRequest):
    """
    Ruta para eliminar un producto del inventario.
    """
    try:
        result = await inventory_manager.delete_product(
            product_id=request.product_id,
            restaurant_id=request.restaurant_id
        )
        if not result:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"detail": "Producto eliminado exitosamente"}
    except Exception as e:
        logging.error("Error eliminando producto: %s", str(e))
        raise HTTPException(status_code=500, detail="Error eliminando producto")
