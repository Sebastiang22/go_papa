import logging
from mysql.connector import Error
import mysql.connector

from core.config import settings

def create_tables():
    """Create all necessary tables in MySQL database if they don't exist."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=settings.db_host,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_database
        )
        print("MySQL Database connection successful")
        
        cursor = connection.cursor()
        try:
            # Create inventory table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id VARCHAR(255) PRIMARY KEY,
                restaurant_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL,
                unit VARCHAR(50) NOT NULL,
                price FLOAT,
                last_updated DATETIME NOT NULL,
                INDEX (restaurant_id)
            )
            """)
            print("Inventory table created successfully")
            
            # Create orders table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(255) PRIMARY KEY,
                enum_order_table VARCHAR(255) NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL,
                price FLOAT DEFAULT 0,
                details TEXT,
                state VARCHAR(50) DEFAULT 'pendiente',
                address VARCHAR(255) NOT NULL,
                user_name VARCHAR(255),
                user_id VARCHAR(255),
                restaurant_id VARCHAR(255) DEFAULT 'go_papa',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                INDEX (enum_order_table),
                INDEX (address),
                INDEX (state),
                INDEX (created_at),
                INDEX (user_id)
            )
            """)
            print("Orders table created successfully")
            
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                address VARCHAR(255),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                INDEX (user_id)
            )
            """)
            print("Users table created successfully")
            
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
            print("Conversations table created successfully")
            
            connection.commit()
            print("All tables created successfully")
            
        except Error as err:
            print(f"Error creating tables: {err}")
        finally:
            cursor.close()
            
    except Error as err:
        print(f"Error connecting to MySQL: {err}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed")


if __name__ == "__main__":
    create_tables()