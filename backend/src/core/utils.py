from datetime import datetime
from pytz import timezone
from docx import Document
import pandas as pd
import timeit
import uuid
import tiktoken
import pdb
import io


def genereta_id() -> str: 
    now = datetime.now()
    str_now = now.strftime("%Y%m%d")
    uuid_id = str(uuid.uuid4())
    chat_id = f'{str_now}-{uuid_id}'
    return chat_id



from datetime import datetime
from typing import Optional, Dict, Any

def generate_order_id(last_order: Optional[Dict[str, Any]], threshold_minutes: int = 60) -> str:
    """
    Genera el ID de pedido basado en un contador que inicia en 100000.
    
    Lógica:
        - Si 'last_order' es None, se retorna el ID inicial "100000".
        - Si existe un 'last_order', se extraen los campos 'created_at' y 'state'.
        - Se calcula la diferencia de tiempo entre la fecha actual y la fecha de creación del último pedido.
        - Si han transcurrido más de 'threshold_minutes' minutos o el estado es "completado", 
          se incrementa el contador en 1 y se retorna ese nuevo valor como ID.
        - Si no se cumple alguna de estas condiciones, se retorna el mismo ID del último pedido.
    
    Parámetros:
        last_order (Optional[Dict[str, Any]]): Diccionario que representa el último pedido registrado, o None si no existe.
        threshold_minutes (int): Umbral en minutos para determinar si se debe generar un nuevo ID. Por defecto es 60.
    
    Retorna:
        str: El ID de pedido generado (como cadena de caracteres) basado en el contador.
    """
    # Usar la hora de Colombia en lugar de datetime.now()
    now_str = current_colombian_time()
    now = datetime.strptime(now_str, '%Y-%m-%d %H:%M:%S')
    
    # Si no existe un pedido previo, se retorna el ID inicial "100000"
    if last_order is None:
        return "100001"
    
    # Extraer la fecha de creación y el estado del último pedido
    last_created_at = last_order.get("created_at")
    last_state = last_order.get("state", "").lower()
    
    try:
        last_created_datetime = datetime.fromisoformat(last_created_at)
    except Exception:
        # Si ocurre un error al parsear la fecha, se utiliza la fecha actual para evitar fallos.
        last_created_datetime = now

    time_diff = now - last_created_datetime
    
    # Se obtiene el contador actual; si no existe, se parte de 100000
    current_counter = int(last_order.get("enum_order_table", "100000"))
    
    # Si han pasado más de 'threshold_minutes' minutos o el pedido está completado, se incrementa el contador.
    if time_diff.total_seconds() > threshold_minutes * 60 or last_state == "completado":
        new_counter = current_counter + 1
        return str(new_counter)
    else:
        # Se reutiliza el ID del último pedido.
        return str(current_counter)


def current_colombian_time() -> str:
    current_time = datetime.now(timezone('America/Bogota')).strftime('%Y-%m-%d %H:%M:%S')
    return current_time

def timeit_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        elapsed_time = end_time - start_time
        return result, elapsed_time
    return wrapper

def count_tokens(texts=None, model_reference="cl100k_base"):   
    if texts:
        encoding = tiktoken.get_encoding(model_reference)
        count = encoding.encode(texts)
        return count
    

def format_conversation_data(documents):
    # Suponiendo que todos son de la misma conversación
    
    if len(documents)==0:
        return None
    
    conversation_id = documents[0]['conversation_id'] if documents else None

    messages = []
    for doc in documents:
        user_msg = doc.get("user_message", {})
        ai_msg = doc.get("ai_message", {})
        
        # Mensaje de usuario
        messages.append({
            "id": doc.get("id"),
            "role": "user",
            "content": user_msg.get("content"),
            "created_at": user_msg.get("created_at")
        })
        
        # Mensaje de la IA
        messages.append({
            "id": doc.get("id"),
            "role": "assistant",
            "content": ai_msg.get("content"),
            "created_at": ai_msg.get("created_at"),
            "rate": doc.get("rate")
        })

    # Ordenar por fecha si es necesario
    messages.sort(key=lambda msg: datetime.fromisoformat(msg["created_at"]))

    return {
        "conversation_id": conversation_id,
        "conversation_name": documents[0].get("conversation_name"),
        "user_id": documents[0].get("user_id"),
        "messages": messages
    }


def extract_text_content(content: bytes) -> str:
    # Asumimos que el contenido está en UTF-8
    return content.decode("utf-8")

def extract_word_content(content: bytes) -> str:
    """
    Extrae el texto de un archivo Word (DOCX) a partir de un objeto de bytes.

    Args:
        content (bytes): Contenido del archivo Word en formato bytes.

    Returns:
        str: Texto extraído del archivo Word.
    """
    # Convertir los bytes en un stream de memoria
    stream = io.BytesIO(content)
    # Abrir el documento usando python-docx
    document = Document(stream)
    
    # Extraer el texto de cada párrafo del documento
    full_text = []
    for paragraph in document.paragraphs:
        full_text.append(paragraph.text)
    
    # Unir los párrafos en un único string, separándolos por saltos de línea
    return "\n".join(full_text)

def extract_excel_content(content: bytes) -> str:
    """
    Lee el contenido de un archivo Excel (en formato bytes) y lo convierte a JSONL,
    donde cada línea representa un registro del Excel.

    Args:
        content (bytes): Contenido del archivo Excel en formato bytes.

    Returns:
        str: Un string en formato JSONL con los registros del Excel.
    """
    try:
        # Crear un objeto BytesIO a partir de los bytes del archivo Excel
        excel_io = io.BytesIO(content)
        # Leer el contenido del Excel en un DataFrame de pandas
        df = pd.read_excel(excel_io)
    except Exception as e:
        raise ValueError(f"Error al leer el archivo Excel: {str(e)}")
    
    # Convertir el DataFrame a JSON Lines (cada registro en una línea)
    jsonl_string = df.to_json(orient="records", lines=True, force_ascii=False)
    return jsonl_string



    
