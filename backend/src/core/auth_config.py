from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional


class AuthSettings(BaseSettings):
    """Configuración para la autenticación con Microsoft Entra ID."""
    
    CLIENT_ID: str
    CLIENT_SECRET: str
    TENANT_ID: str
    FRONTEND_URL: str
    REDIRECT_PATH: str = "/auth/callback"
    AUTHORITY: Optional[str] = None
    SCOPES: List[str] = ["https://graph.microsoft.com/.default"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Permitir variables adicionales en .env
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.AUTHORITY:
            self.AUTHORITY = f"https://login.microsoftonline.com/{self.TENANT_ID}"


@lru_cache()
def get_auth_settings() -> AuthSettings:
    """Retorna una instancia cacheada de la configuración de autenticación."""
    return AuthSettings() 