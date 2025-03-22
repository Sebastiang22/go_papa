from pydantic import BaseModel
from typing import Optional, Literal
from fastapi import UploadFile


class ResponseHTTPChat(BaseModel):
    id: str
    text: str
class ResponseHTTPStartConversation(BaseModel):
    user_id: str
    conversation_id: str
    conversation_name: str
class RequestHTTPStartConversation(BaseModel):
    user_id: str
    conversation_name: str
class RequestHTTPChat(BaseModel):
    user_id: str
    conversation_id: str
    conversation_name: str
    query: str
    restaurant_name:Optional[Literal["go_papa"]] = None

class RequestHTTPVote(BaseModel):
    id: str
    thread_id: str
    rate:bool

class ResponseHTTPVote(BaseModel):
    id: str
    text: str
    state: bool
    
class RequestHTTPSessions(BaseModel):
    user_id: str
class ResponseHTTPSessions(BaseModel):
    user_id: str
    sessions:list
    
class RequestHTTPOneSession(BaseModel):
    conversation_id: str
class ResponseHTTPOneSession(BaseModel):
    conversation_id: str
    conversation_name:str
    user_id:str
    messages: list
    
class RequestHTTPUpdateState(BaseModel):
    order_id: str
    state: Literal["pendiente","en preparación","completado"] = "pendiente"
    partition_key: Optional[str] = None

# Nuevos modelos para la gestión de usuarios
class RequestHTTPCreateUser(BaseModel):
    user_id: str
    name: str
    address: str

class RequestHTTPGetUser(BaseModel):
    user_id: str

class ResponseHTTPUser(BaseModel):
    user_id: str
    name: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime

# IMPORTANTE: Importar MySQLInventoryManager en lugar de AzureServices
from core.mysql_inventory_manager import MySQLInventoryManager

# Instancia del administrador de inventario
inventory_manager = MySQLInventoryManager()  # Usar MySQLInventoryManager en lugar de AzureServices.AsyncInventoryManager

# Definición de modelos Pydantic para las solicitudes y respuestas

class Product(BaseModel):
    id: str
    restaurant_id: str
    name: str
    quantity: int
    unit: str
    price: Optional[float] = None
    last_updated: str

class AddProductRequest(BaseModel):
    restaurant_id: str
    name: str
    quantity: int
    unit: str
    price: Optional[float] = None

class UpdateProductRequest(BaseModel):
    product_id: str
    restaurant_id: str
    name: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    price: Optional[float] = None

class DeleteProductRequest(BaseModel):
    product_id: str
    restaurant_id: str
    
    
    
    #
