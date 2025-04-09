from typing import Optional, List, Dict, Any, Tuple
import json
import aiomysql
from aiomysql import Error
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from core.config import settings
from core.db_pool import DBConnectionPool
from core.utils import current_colombian_time



class MySQLSaver:
    def __init__(self):
        """Initialize the MySQL connection using shared pool."""
        self.db_pool = DBConnectionPool()
    
    async def _create_tables(self):
        """Create necessary tables if they don't exist."""
        pool = await self.db_pool.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    # Create conversations table
                    await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        conversation_id VARCHAR(255) NOT NULL,
                        conversation_name VARCHAR(255) NOT NULL,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        user_message_content TEXT NOT NULL,
                        user_message_kwargs JSON,
                        user_message_metadata JSON,
                        user_message_id VARCHAR(255),
                        ai_message_content TEXT NOT NULL,
                        ai_message_kwargs JSON,
                        ai_message_metadata JSON,
                        ai_message_id VARCHAR(255),
                        rate BOOLEAN DEFAULT FALSE,
                        INDEX (conversation_id),
                        INDEX (user_id)
                    )
                    """)
                    await conn.commit()
                    print("Table created successfully")
                except Error as err:
                    print(f"Error creating tables: {err}")
    
    def _message_to_dict(self, message: BaseMessage) -> dict:
        """Convert a BaseMessage to a dictionary."""
        return {
            "content": message.content,
            "additional_kwargs": getattr(message, "additional_kwargs", {}),
            "response_metadata": getattr(message, "response_metadata", {}),
            "id": getattr(message, "id", ""),
            "created_at": current_colombian_time()
        }
    
    async def save_conversation(self, user_message: BaseMessage, ai_message: BaseMessage, 
                              conversation_id: str, conversation_name: str, user_id: str) -> int:
        """Save conversation to MySQL database."""
        pool = await self.db_pool.get_pool()
        
        user_msg_dict = self._message_to_dict(user_message)
        ai_msg_dict = self._message_to_dict(ai_message)
        
        # Generate today's date as conversation_id
        today_date = current_colombian_time().split()[0]  # Obtener solo la fecha (YYYY-MM-DD)
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    query = """
                    INSERT INTO conversations (
                        user_id, conversation_id, created_at, 
                        user_message_content, ai_message_content, rate
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    now = datetime.strptime(current_colombian_time(), '%Y-%m-%d %H:%M:%S')
                    
                    await cursor.execute(query, (
                        user_id,
                        today_date,  # Using today's date as conversation_id
                        now,
                        user_msg_dict["content"],
                        ai_msg_dict["content"],
                        False
                    ))
                    
                    await conn.commit()
                    last_id = cursor.lastrowid
                    print(f"Conversation saved with ID: {last_id}")
                    return last_id
                except Error as err:
                    await conn.rollback()
                    print(f"Error saving conversation: {err}")
                    return 0
    
    async def get_conversation_history(self, user_id: str) -> List[BaseMessage]:
        """Retrieve conversation history for a user from the current day."""
        pool = await self.db_pool.get_pool()
        
        async with pool.acquire() as conn:
            # Importante: Asegurarse de que la conexión no esté en modo autocommit
            conn.autocommit(False)
            
            # Forzar un commit de cualquier transacción pendiente
            await conn.commit()
            
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    # Get today's date range
                    today = datetime.now().date()
                    today_start = datetime.combine(today, datetime.min.time())
                    today_end = datetime.combine(today, datetime.max.time())
                    
                    # Ordenar por created_at para obtener los mensajes en orden cronológico
                    # y limitar a los últimos N mensajes (ajustar según necesidad)
                    query = """
                    SELECT * FROM conversations 
                    WHERE user_id = %s 
                    AND created_at BETWEEN %s AND %s
                    ORDER BY created_at DESC 
                    LIMIT 20
                    """
                    
                    await cursor.execute(query, (user_id, today_start, today_end))
                    rows = await cursor.fetchall()
                    
                    # Importante: Cerrar explícitamente el cursor y hacer commit
                    await cursor.close()
                    await conn.commit()
                    
                    # Convertir los resultados en mensajes
                    messages = []
                    for row in reversed(rows):  # Invertir para orden cronológico
                        # Crear mensaje del usuario
                        user_msg = HumanMessage(
                            content=row["user_message_content"]
                        )
                        
                        # Crear mensaje de la IA
                        ai_msg = AIMessage(
                            content=row["ai_message_content"]
                        )
                        
                        messages.append(user_msg)
                        messages.append(ai_msg)
                    
                    return messages
                    
                except Exception as e:
                    print(f"Error retrieving conversation history: {e}")
                    # En caso de error, asegurarse de hacer rollback
                    await conn.rollback()
                    return []
    
    async def close(self):
        """Cierra el pool de conexiones."""
        if self.db_pool:
            await self.db_pool.close()