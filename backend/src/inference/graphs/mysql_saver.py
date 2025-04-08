from typing import Optional, List, Dict, Any, Tuple
import json
import aiomysql
from aiomysql import Error
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from core.config import settings
from core.db_pool import DBConnectionPool


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
            "created_at": datetime.now().isoformat()
        }
    
    async def save_conversation(self, user_message: BaseMessage, ai_message: BaseMessage, 
                              conversation_id: str, conversation_name: str, user_id: str) -> int:
        """Save conversation to MySQL database."""
        pool = await self.db_pool.get_pool()
        
        user_msg_dict = self._message_to_dict(user_message)
        ai_msg_dict = self._message_to_dict(ai_message)
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    query = """
                    INSERT INTO conversations (
                        user_id, conversation_id, conversation_name, 
                        created_at, updated_at, user_message_content, user_message_kwargs, 
                        user_message_metadata, user_message_id, ai_message_content, 
                        ai_message_kwargs, ai_message_metadata, ai_message_id, rate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    now = datetime.now()
                    
                    await cursor.execute(query, (
                        user_id,
                        conversation_id,
                        conversation_name,
                        now,
                        now,
                        user_msg_dict["content"],
                        json.dumps(user_msg_dict["additional_kwargs"]),
                        json.dumps(user_msg_dict["response_metadata"]),
                        user_msg_dict["id"],
                        ai_msg_dict["content"],
                        json.dumps(ai_msg_dict["additional_kwargs"]),
                        json.dumps(ai_msg_dict["response_metadata"]),
                        ai_msg_dict["id"],
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
    
    async def get_conversation_history(self, user_id: str,max_messages = 10) -> List[Dict]:
        """Retrieve conversation history from MySQL database."""
        pool = await self.db_pool.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    query = """
                    SELECT * FROM conversations 
                    WHERE user_id = %s
                    ORDER BY id DESC
                    LIMIT %s
                    """
                    
                    await cursor.execute(query, (user_id, max_messages))
                    await conn.commit()
                    docs = await cursor.fetchall()
                    
                    history = []
                    
                    print("\nHistorial de conversación:")
                    print("-" * 50)
                    
                    for doc in reversed(docs):
                        # Print and create HumanMessage
                        print(f"\033[0;37mUsuario: {doc['user_message_content']}\033[0m")  # Blanco
                        history.append(HumanMessage(
                            content=doc["user_message_content"],
                            id=doc["user_message_id"]
                        ))
                        
                        # Print and create AIMessage
                        # Modificar la forma de imprimir los mensajes
                        try:
                            print(f"IA: {doc['ai_message_content']}")  # Removido el color y emoji
                        except UnicodeEncodeError:
                            # Si hay error de codificación, intentar limpiar caracteres especiales
                            cleaned_message = doc['ai_message_content'].encode('ascii', 'ignore').decode('ascii')
                            print(f"IA: {cleaned_message}")
                        print("-" * 50)
                        history.append(AIMessage(
                            content=doc["ai_message_content"],
                            id=doc["ai_message_id"]
                        ))
                    
                    print(f"Total de mensajes: {len(history)}")
                    return history
                except Error as err:
                    print(f"Error retrieving conversation history: {err}")
                    return []
    
    async def close(self):
        """Cierra el pool de conexiones."""
        if self.db_pool:
            await self.db_pool.close()