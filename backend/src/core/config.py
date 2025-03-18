from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(), override=True)

class Settings():
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")
        
        # Database Configuration
        self.db_user: str = os.getenv("DB_USER")
        self.db_password: str = os.getenv("DB_PASSWORD")
        self.db_host: str = os.getenv("DB_HOST")
        self.db_database: str = os.getenv("DB_DATABASE")
        
settings = Settings()