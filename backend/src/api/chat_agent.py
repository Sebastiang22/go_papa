from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from core.schema_http import (
    RequestHTTPChat, ResponseHTTPChat,
    RequestHTTPVote, ResponseHTTPVote,
    ResponseHTTPStartConversation, RequestHTTPStartConversation,RequestHTTPUpdateState,
    RequestHTTPSessions, ResponseHTTPSessions,
    ResponseHTTPOneSession, RequestHTTPOneSession
)
from core.utils import genereta_id
import pdb
from inference.graphs.restaurant_graph import RestaurantChatAgent
from langchain_core.messages import HumanMessage
from core.utils import extract_text_content,extract_word_content,extract_excel_content
# from core.schema_services import AzureServices
from inference.graphs.mysql_saver import MySQLSaver
from core.mysql_order_manager import MySQLOrderManager
import os

chat_agent_router = APIRouter()

# Declarar explícitamente la variable global
restaurant_chat_agent = None

@chat_agent_router.post("/message", response_model=ResponseHTTPChat)
async def endpoint_message(request: RequestHTTPChat):
    """
    Endpoint para procesar el mensaje y generar respuesta.
    """
    global restaurant_chat_agent
    
    if restaurant_chat_agent is None:
        restaurant_chat_agent = RestaurantChatAgent()

    new_state, message_id = await restaurant_chat_agent.invoke_flow(
        user_input=request.query,
        conversation_id=request.conversation_id,
        conversation_name=request.conversation_name,
        user_id=request.user_id,
        restaurant_name=request.restaurant_name
    )
    final_msg = new_state["messages"][-1]
    
    return {"id": message_id, "text": final_msg.content}
