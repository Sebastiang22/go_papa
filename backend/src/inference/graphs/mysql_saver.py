from typing import Optional, List, Dict, Any, Tuple
import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from core.config import settings


class MySQLSaver:
    def __init__(self):
        """Initialize the MySQL connection and create table if it doesn't exist."""
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish connection to MySQL database using settings from config."""
        try:
            self.connection = mysql.connector.connect(
                host=settings.db_host,
                user=settings.db_user,
                password=settings.db_password,
                database=settings.db_database
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        if self.connection is None or not self.connection.is_connected():
            self._connect()
            if self.connection is None or not self.connection.is_connected():
                print("Failed to connect to MySQL database")
                return
        
        cursor = self.connection.cursor()
        try:
            # Create conversations table
            cursor.execute("""
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
            self.connection.commit()
            print("Table created successfully")
        except Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
    
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
        if self.connection is None or not self.connection.is_connected():
            self._connect()
            if self.connection is None or not self.connection.is_connected():
                print("Failed to connect to MySQL database")
                return 0
        
        user_msg_dict = self._message_to_dict(user_message)
        ai_msg_dict = self._message_to_dict(ai_message)
        
        cursor = self.connection.cursor()
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
            
            cursor.execute(query, (
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
            
            self.connection.commit()
            last_id = cursor.lastrowid
            print(f"Conversation saved with ID: {last_id}")
            return last_id
        except Error as err:
            print(f"Error saving conversation: {err}")
            return 0
        finally:
            cursor.close()
    
    async def get_conversation_history(self, user_id: str, max_messages: int = 20) -> List[BaseMessage]:
        """Retrieve conversation history from MySQL database."""
        if self.connection is None or not self.connection.is_connected():
            self._connect()
            if self.connection is None or not self.connection.is_connected():
                print("Failed to connect to MySQL database")
                return []
        
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = """
            SELECT * FROM conversations 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            cursor.execute(query, (user_id, max_messages))
            docs = cursor.fetchall()
            
            history = []
            
            for doc in reversed(docs):  # Orden cronológico
                # Create HumanMessage
                history.append(HumanMessage(
                    content=doc["user_message_content"],
                    additional_kwargs=json.loads(doc["user_message_kwargs"]),
                    response_metadata=json.loads(doc["user_message_metadata"]),
                    id=doc["user_message_id"]
                ))
                
                # Create AIMessage
                history.append(AIMessage(
                    content=doc["ai_message_content"],
                    additional_kwargs=json.loads(doc["ai_message_kwargs"]),
                    response_metadata=json.loads(doc["ai_message_metadata"]),
                    id=doc["ai_message_id"]
                ))
            
            return history
        except Error as err:
            print(f"Error retrieving conversation history: {err}")
            return []
        finally:
            cursor.close()