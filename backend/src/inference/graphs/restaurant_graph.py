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
from inference.tools.restaurant_tools import get_menu_tool,confirm_order_tool,get_order_status_tool
import json
import asyncio
from langchain_openai import ChatOpenAI

######################################################
# 1) Estado del Bot (hereda messages)
######################################################
class RestaurantStateDict(TypedDict):
    thread_id: Optional[str]
    restaurant_name: Optional[str]

class RestaurantState(MessagesState):
    thread_id: Optional[str] = None
    restaurant_name: Optional[str] = None
        # - consultar_menu:

        #     Utiliza esta herramienta para mostrar el menú actualizado del restaurante.
        #     Informa al cliente que la consulta puede tardar unos segundos.

SYSTEM_PROMPT =     """
        Fecha y Hora Actual: {{fecha-hora}}
        Eres un asistente de IA especializado en atención a clientes en nuestro restaurante. Tu misión es guiar a los comensales en el proceso de seleccionar y confirmar cada producto o plato de su pedido.
        Responde de manera amigable usando emojis de vez en cuando.
        Debes indagar o preguntar los datos necesarios para realizar la orden.

        Herramientas disponibles:


        - confirmar_pedido:

            Esta herramienta se utiliza para registrar y actualizar el documento del pedido en MySQL cada vez que se confirme un producto o plato.
            Antes de llamar a esta herramienta, debes llamar a la herramienta get_menu_tool para obtener la disponibilidad del menú en tiempo real y el id del producto a comprar. (a menos que ya tengas el conocimiento de esos datos).
            Importante: Cada vez que el cliente confirme un producto, debes llamar a esta herramienta una unica vez por producto, con un input que sean exactamente los siguientes campos:
                product_id : id del producto (que obtienes llamando a la tool get_menu_tool)
                product_name: nombre del producto (que obtienes llamando a la tool get_menu_tool)
                quantity: cantidad de productos a comprar (que debes preguntar al cliente)
                details: detalles adicionales del pedido (debes agregar si el cliente las menciona, de lo contrario puedes dejarlo en blanco)
                address: dirección de entrega del pedido (debes preguntar al cliente)
                user_name: nombre del cliente (debes preguntar al cliente)
            Si en la conversación notas que ya se realizo un pedido identico o con el mensaje exactamente igual deber preguntar al cliente si desea realizarlo nuevamente (ya que probablemente haya sido un accidente).
            
        - get_menu_tool:

            Esta herramienta se utiliza para obtener la disponibilidad del menú en tiempo real.
            Importante: Cada vez que el cliente pregunte por el menú, debes llamar a esta herramienta sin embargo no debes mencionar la cantidad de platos disponibles en el inventario.
            Ofrece unicamente los productos que tengan unidades disponibles pero nunca menciones la cantidad que hay, amenos que el usaurio mencione ser el 'administrador' o 'admin' solo en esos casos si puedes mencionar la cantidad del inventario.
            
        - get_order_status_tool:
            Esta herramienta se utiliza para obtener el estado del pedido completo para la dirección del cliente. Únicamente recibe una dirección que puede estar en los ultimos mensajes de la conversacion o se puede preguntar al cliente y devuelve un diccionario con la informacion del pedido.
            Usa esta herramienta cuando el cliente pregunte como va su pedido o cuando quiera ver el estado de su pedido o sencillamente quiera ver qué han pedido hasta el momento.
        Instrucciones y Reglas de Interacción:

        Saludo y cortesía: Inicia cada conversación saludando de forma amistosa, amable y profesional.
        Indagación: Pregunta al cliente si desea consultar el menú, obtener detalles sobre algún plato o confirmar un producto.
        
        Proceso de pedido:
            Una vez que el cliente seleccione un producto o plato y preguntes confirmando su elección, llama a la herramienta confirmar_pedido utilizando el formato exacto especificado anteriormente.
            
        Claridad y veracidad: Proporciona respuestas claras y precisas. Si ocurre algún error o la herramienta no procesa correctamente la solicitud, informa al cliente de forma amable.
        Actúa de manera muy servicial preguntando si hay alguna otra orden o pedido que quiera realizar, preguntando por bebidas u otros platos que deseen ordenar.
        
        
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

    system_msg = SystemMessage(content=SYSTEM_PROMPT.replace("{{fecha-hora}}",datetime.now().isoformat()))
    new_messages = [system_msg] + state["messages"][-max_messages:]

    # 1) Preparamos el LLM que tenga "search_tool" enlazado
    llm_raw = ChatOpenAI(api_key=SecretStr(settings.openai_api_key),
                        model=settings.openai_model)
    # bind_tools => el LLM sabe formatear la tool call como 
    # {"tool_calls": [{"name": "search_tool", "args": "..."}]}
    llm_with_tools = llm_raw.bind_tools([confirm_order_tool,get_menu_tool,get_order_status_tool])#

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
                if "restaurant_name" in arguments and not (arguments["restaurant_name"] == "Macchiato" or arguments["restaurant_name"] is None):
                    # If restaurant_name is not valid, use the default
                    arguments["restaurant_name"] = state.get("restaurant_name") if state.get("restaurant_name") else "Macchiato"
                else:
                    # If restaurant_name is not in arguments, add it
                    arguments["restaurant_name"] = state.get("restaurant_name") if state.get("restaurant_name") else "Macchiato"
                tool_call["args"] = arguments
                tool_calls_verified.append(tool_call)

            elif tool_call["name"] == "confirm_order_tool":
                print(f"\033[32m Tool Call: {tool_call['name']}  conversation_id {state['thread_id']}\033[0m")

                arguments = tool_call["args"]
                arguments["restaurant_id"] = state.get("restaurant_name") if state.get("restaurant_name") else "Macchiato"
                tool_call["args"] = arguments
                tool_calls_verified.append(tool_call)

            elif tool_call["name"] == "get_order_status_tool":
                print(f"\033[32m Tool Call: {tool_call['name']}  conversation_id {state['thread_id']}\033[0m")

                arguments = tool_call["args"]
                arguments["restaurant_id"] = state.get("restaurant_name") if state.get("restaurant_name") else "Macchiato"
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
        graph.add_node("ToolsNode", ToolNode([confirm_order_tool, get_menu_tool,get_order_status_tool]))

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
        print(history_messages)
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

        # Solicitud APi Whatsapp
        # requests
        # - endpoint: https://api.whatsapp.com/send
        # - method: POST
        # - body: {message:""}
        #

        return new_state, doc_id



        