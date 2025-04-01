from typing import Optional, Literal, List, Any, Union, TypedDict
from pydantic import SecretStr

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage, AnyMessage
from langgraph.graph import StateGraph, START, MessagesState, END
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.prebuilt import  ToolNode

from core.config import settings
from inference.graphs.mysql_saver import MySQLSaver
from core import utils
import pdb
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
from datetime import datetime
from inference.tools.restaurant_tools import get_menu_tool,confirm_order_tool,get_order_status_tool,send_menu_pdf_tool
import json
import asyncio
from langchain_openai import ChatOpenAI
import sys
import asyncio

# Si estamos en Python 3.11 o superior, parcheamos create_task para ignorar el argumento 'context'
if sys.version_info >= (3, 11):
    original_create_task = asyncio.create_task

    def create_task_patch(coro, *, context=None, name=None):
        # Ignoramos 'context' si se pasa, pero pasamos 'name'
        return original_create_task(coro, name=name)

    asyncio.create_task = create_task_patch

######################################################
# 1) Estado del Bot (hereda messages)
######################################################
class RestaurantStateDict(TypedDict):
    thread_id: Optional[str]
    restaurant_name: Optional[str]
    user_id: Optional[str]

class RestaurantState(MessagesState):
    thread_id: Optional[str] = None
    restaurant_name: Optional[str] = None
    user_id: Optional[str] = None
        # - consultar_menu:

        #     Utiliza esta herramienta para mostrar el menú actualizado del restaurante.
        #     Informa al cliente que la consulta puede tardar unos segundos.

SYSTEM_PROMPT =     """
Fecha y Hora Actual: {{fecha-hora}}

Eres un asistente de IA especializado en la atención a clientes para nuestro restaurante {{restaurant_name}}. Tu misión es guiar a los comensales en el proceso de selección y confirmación de cada producto o plato de su pedido. Responde de manera amigable, utilizando emojis ocasionalmente, y siempre indaga los datos necesarios para completar la orden.

*Información del Cliente:*
{{user_info}}

---

### Herramientas Disponibles

1. *confirm_order_tool*  
   - *Función:* Registra y actualiza el documento del pedido en MySQL cada vez que se confirme un producto o plato.  
   - *Procedimiento:*  
     - Antes de usar esta herramienta, llama a *get_menu_tool* para obtener en tiempo real:
       - La disponibilidad del producto.
       - El id y nombre del producto.
       - El precio unitario.
     - *Datos requeridos para confirmar un producto:*  
       - *product_id:* ID obtenido de get_menu_tool.  
       - *product_name:* Nombre obtenido de get_menu_tool.  
       - *quantity:* Cantidad a comprar (preguntar al cliente).  
       - *price:* Precio total (cantidad × precio unitario del producto).  
       - *observaciones:* Detalles adicionales específicos del producto (añadir si el cliente los menciona, o dejar en blanco).
       - *address:* Dirección de entrega (preguntar al cliente).  
       - *user_name:* Nombre del cliente (preguntar al cliente).  
   - *Consideraciones adicionales:*  
     - Si se detecta que ya se realizó un pedido idéntico o con el mismo mensaje, pregunta al cliente si desea repetirlo (podría tratarse de un error).  
     - *Salchipapas en el menú:*  
       - Pueden ser del tipo "<nombre salchipapa> x2" o "<nombre salchipapa> familiar".  
       - Si el cliente solicita una salchipapa "x2", por defecto registra la cantidad como 1, a menos que el cliente especifique explícitamente que quiere dos unidades.  


2. *get_menu_tool*  
   - *Función:* Consulta la disponibilidad del menú en tiempo real.  
   - *Uso:*  
     - Llama a esta herramienta siempre antes de confirmar un pedido a menos que ya tengas la informacion necesaria del producto para realizar el pedido.  
     - Solo ofrece productos con unidades disponibles en el inventario.  
     - No menciones la cantidad exacta en inventario ni ofrezcas productos que estén agotados.

3. *get_order_status_tool*  
   - *Función:* Consulta el estado del pedido de un cliente.  
   - *Uso:*  
     - Llama a esta herramienta cuando el cliente pregunte por el estado de su pedido o su progreso.  
     - Para su uso, solicita al cliente su dirección. Si no la proporciona, pregunta primero por ella.  
     - Presenta la información de forma clara y amigable.

4. *send_menu_pdf_tool*  
   - *Función:* Envía las fotos del menú completo al cliente.  
   - *Uso:*  
     - Llama a esta herramienta cuando el cliente solicite explícitamente ver el menú.  
     - Informa al cliente que ha recibido el menú y procede a tomar su pedido.

---

### Flujo de Conversación y Proceso de Pedido

1. *Saludo y Cortesía:*  
   - Inicia cada conversación con un saludo amigable, profesional y cálido.

2. *Verificación de Órdenes Pendientes:*  
   - Si el cliente no tiene órdenes pendientes (verifica con *get_order_status_tool*), muestra el menú y ayuda a iniciar un pedido.  
   - Si hay órdenes pendientes, informa al cliente sobre su estado y pregunta si desea agregar más productos.

3. *Proceso para Confirmar un Pedido:*  
   - Antes de confirmar cualquier producto, *verifica la disponibilidad* usando *get_menu_tool*.  
   - Una vez confirmada la disponibilidad y seleccionado el producto, confirma la elección con el cliente y llama a *confirm_order_tool* con los datos requeridos.  
   - Si el cliente tiene una orden en curso y desea agregar productos, asegúrate de:
     - Usar la misma dirección y nombre del cliente (a menos que la orden esté completada).  
     - No agregar productos si el pedido está "en entrega"; en ese caso, sugiere iniciar un nuevo pedido.
   - Si el cliente pide ver el menú, utiliza *send_menu_pdf_tool* y luego continúa el proceso de toma de pedido.

4. *Claridad y Asistencia:*  
   - Responde de forma clara, precisa y amable.  
   - Si ocurre algún error o la herramienta falla, informa al cliente de manera comprensiva y brinda alternativas.  
   - Siempre ofrece ayuda adicional preguntando si el cliente desea agregar bebidas u otros productos.

---

### Notas Adicionales

- *Consistencia:* Asegúrate de usar términos y nombres de herramientas de forma consistente (por ejemplo, "confirm_order_tool" en lugar de "confirmar_pedido").  
- *Interacción Amigable:* Aprovecha el uso de emojis y un lenguaje cercano para mejorar la experiencia del cliente.
        
        """

######################################################
# 2) main_agent_node (asíncrono) + tools usage
######################################################
async def main_agent_node(state: RestaurantState) -> RestaurantState:
    """
    1) Inyecta system prompt
    2) Llama repetidamente al LLM (con .bind_tools([...]))
       Si el LLM produce tool_calls (ej: name="search_tool"), se ejecutan
       y se añade un AIMessage con los resultados. 
       Se repite hasta que no haya más tool_calls.
    3) Devuelve el estado final
    """
    # Preparar la conversacion
    max_messages = 10 
    # Obtener información del usuario si está disponible en el estado
    user_info = ""
    user_id = state["user_id"]
        
        # Importar el gestor de usuarios
    from core.mysql_user_manager import MySQLUserManager
    user_manager = MySQLUserManager()
    
    # Obtener información del usuario
    user_data = await user_manager.get_user(user_id)
    print(f"Información del Usuario: {user_data}")
    if user_data:
        user_info = (
            f"Nombre: {user_data.get('name', 'No disponible')}\n"
            f"Dirección: {user_data.get('address', 'No disponible')}"
            f"user_id: {user_id}\n"
            
        )

    # Inyectar la información del usuario en el prompt del sistema
    system_prompt_with_user = SYSTEM_PROMPT.replace("{{fecha-hora}}", datetime.now().isoformat()).replace("{{user_info}}", user_info).replace("{{restaurant_name}}", state.get("restaurant_name", "go_papa"))
    system_msg = SystemMessage(content=system_prompt_with_user)
    new_messages = [system_msg] + state["messages"][-max_messages:]

    # 1) Preparamos el LLM que tenga "search_tool" enlazado
    llm_raw = ChatOpenAI(api_key=SecretStr(settings.openai_api_key),
                        model=settings.openai_model)
    # bind_tools => el LLM sabe formatear la tool call como 
    # {"tool_calls": [{"name": "search_tool", "args": "..."}]}
    # In main_agent_node function
    llm_with_tools = llm_raw.bind_tools(
    tools=[confirm_order_tool, get_menu_tool, get_order_status_tool, send_menu_pdf_tool]
        )

    # 2) Bucle: Llamamos al LLM -> revisamos tool_calls -> ejecutamos -> loop
    # while True:
    #     # Llamado sincrónico al LLM

    response_msg = llm_with_tools.invoke(new_messages)
    #     # Añadimos su output al historial
    tool_calls_verified = []
    if isinstance(response_msg, AIMessage) and hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
        for tool_call in response_msg.tool_calls:

            if tool_call["name"] == "get_menu_tool":
                print(f"\033[32m Tool Call: {tool_call['name']}  conversation_id {state['thread_id']}\033[0m")

                arguments = tool_call["args"]
                # Ensure restaurant_name is always a valid value, not user input
                if "restaurant_name" in arguments and not (arguments["restaurant_name"] == "go_papa" or arguments["restaurant_name"] is None):
                    # If restaurant_name is not valid, use the default
                    arguments["restaurant_name"] = state.get("restaurant_name") if state.get("restaurant_name") else "go_papa"
                else:
                    # If restaurant_name is not in arguments, add it
                    arguments["restaurant_name"] = state.get("restaurant_name") if state.get("restaurant_name") else "go_papa"
                tool_call["args"] = arguments
                tool_calls_verified.append(tool_call)

            elif tool_call["name"] == "confirm_order_tool":
                print(f"\033[32m Tool Call: {tool_call['name']}  conversation_id {state['thread_id']}\033[0m")

                arguments = tool_call["args"]
                arguments["restaurant_id"] = state.get("restaurant_name") if state.get("restaurant_name") else "go_papa"
                arguments["user_id"] = state.get("user_id")
                # Asegurarse de que observaciones esté presente en los argumentos incluso si es None
                if "observaciones" not in arguments:
                    arguments["observaciones"] = None
                tool_call["args"] = arguments
                tool_calls_verified.append(tool_call)

            elif tool_call["name"] == "get_order_status_tool":
                print(f"\033[32m Tool Call: {tool_call['name']}  conversation_id {state['thread_id']}\033[0m")

                arguments = tool_call["args"]
                arguments["restaurant_id"] = state.get("restaurant_name") if state.get("restaurant_name") else "go_papa"
                tool_call["args"] = arguments
                tool_calls_verified.append(tool_call)

            elif tool_call["name"] == "send_menu_pdf_tool":
                print(f"\033[32m Tool Call: {tool_call['name']}  conversation_id {state['thread_id']}\033[0m")

                arguments = tool_call["args"]
                # Asegurarse de que user_id esté presente en los argumentos
                if "user_id" not in arguments or not arguments["user_id"]:
                    arguments["user_id"] = state.get("user_id")
                tool_call["args"] = arguments
                tool_calls_verified.append(tool_call)

            else:
                tool_calls_verified.append(tool_call)

        response_msg.tool_calls = tool_calls_verified 
        
    new_messages.append(response_msg)

    # 3) Retornar el estado final
    return {
        "messages": new_messages,
        "thread_id": state["thread_id"],
        "restaurant_name": state["restaurant_name"]
    }

def route_after_agent(
        state: RestaurantState,
    ) -> Literal[
        "AgentNode",
        "ToolsNode",
        "__end__"]: 
        
    """Direcciona el siguiente nodo tras la acción del agente.

    Esta función determina el siguiente paso en el proceso de investigación basándose en el
    último mensaje en el estado. Maneja tres escenarios principales:

    
    1. Scraper en Ecommerce de Bata
    """
    last_message = state["messages"][-1]

    # "If for some reason the last message is not an AIMessage (due to a bug or unexpected behavior elsewhere in the code),
    # it ensures the system doesn't crash but instead tries to recover by calling the agent model again.
    if not isinstance(last_message, AIMessage):
        return "AgentNode"
    # If the "Into" tool was called, then the model provided its extraction output. Reflect on the result
    
    if last_message.tool_calls:
            return "ToolsNode"
        # if last_message.tool_calls and last_message.tool_calls[0]["name"] == "scrape_tool":
        #     return "WebScraperNode"
        # The last message is a tool call that is not "Info" (extraction output)
    else:
        return "__end__"

######################################################
# 3) Construir el Graph + checkpoint
######################################################
class RestaurantChatAgent:
    def __init__(self):
        # 1) Creamos un StateGraph con RestaurantState
        graph = StateGraph(state_schema=RestaurantState)

        # 2) Añadimos un solo nodo (main_agent_node)
        graph.add_node("AgentNode", main_agent_node)
        graph.add_node("ToolsNode", ToolNode([confirm_order_tool, get_menu_tool, get_order_status_tool, send_menu_pdf_tool]))

        # 3)
        graph.add_edge(START, "AgentNode")
        graph.add_conditional_edges("AgentNode", route_after_agent)
        graph.add_edge("ToolsNode", "AgentNode")
        # graph.add_edge("AgentNode", END)

        # 4) Saver con MySQL
        self.mysql_saver = MySQLSaver()

        # 5) Compilar
        self.app = graph.compile() 

        # (Opcional) Generar imagen del grafo
        # image_data = self.app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        # image = Image(image_data)
        # with open("graph_image.png", "wb") as f:
        #     f.write(image.data)

    async def invoke_flow(
    self,
    user_input: str,  # Ahora recibimos el input directo
    conversation_id: str,
    conversation_name: str,
    user_id: str,
    restaurant_name: Optional[str]
    ) -> tuple[RestaurantState, str]:
        # 1. Recuperar historial previo
        history_messages = await self.mysql_saver.get_conversation_history(
            user_id
        )
        # 2. Construir lista de mensajes completa
        new_human_message = HumanMessage(
            content=user_input,
            id=utils.genereta_id(),
            response_metadata={"timestamp": datetime.now().isoformat()}
        )
        all_messages = history_messages + [new_human_message]
        # 3. Ejecutar el flujo
        new_state = await self.app.ainvoke(
            {
                "messages": all_messages,
                "thread_id": conversation_id,
                "restaurant_name": restaurant_name,
                "user_id": user_id,
            },
            config={"configurable": {"thread_id": conversation_id, "user_id": user_id}},
        )

        # 4. Extraer y guardar solo el último intercambio
        new_messages = new_state["messages"][len(all_messages):]
        new_ai_messages = [msg for msg in new_messages if isinstance(msg, AIMessage)]
        if not new_ai_messages:
            raise ValueError("No se generó respuesta de AI")
        ai_response = new_ai_messages[-1]

        doc_id = await self.mysql_saver.save_conversation(
            user_message=new_human_message,
            ai_message=ai_response,
            conversation_id=conversation_id,
            conversation_name=conversation_name,
            user_id=user_id
        )

        # Return properly typed RestaurantState and string ID
        return RestaurantState(messages=new_state["messages"],
                             thread_id=conversation_id,
                             restaurant_name=restaurant_name), str(doc_id)



        