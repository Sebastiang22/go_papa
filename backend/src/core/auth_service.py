from msal import ConfidentialClientApplication
import requests
from typing import Tuple, Dict, Any, Optional
import logging

from core.auth_config import get_auth_settings

logger = logging.getLogger(__name__)


class AuthService:
    """Servicio para la autenticación con Microsoft Entra ID."""
    
    def __init__(self):
        self.settings = get_auth_settings()
        self.client_instance = self._create_msal_app()
    
    def _create_msal_app(self) -> ConfidentialClientApplication:
        """Crea y configura la aplicación MSAL para autenticación."""
        try:
            return ConfidentialClientApplication(
                client_id=self.settings.CLIENT_ID,
                client_credential=self.settings.CLIENT_SECRET,
                authority=self.settings.AUTHORITY
            )
        except Exception as e:
            logger.error(f"Error al crear la aplicación MSAL: {e}")
            raise
    
    def get_auth_url(self, prompt: Optional[str] = None) -> str:
        """Genera la URL de autorización para el inicio de sesión.
        
        Args:
            prompt: Tipo de prompt para la autenticación (ej: 'login')
            
        Returns:
            URL de autorización para redireccionar al usuario
        """
        try:
            kwargs = {"prompt": prompt} if prompt else {}
            return self.client_instance.get_authorization_request_url(
                scopes=self.settings.SCOPES,
                redirect_uri=f"{self.settings.FRONTEND_URL}{self.settings.REDIRECT_PATH}",
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error al generar URL de autorización: {e}")
            raise
    
    def acquire_token_by_code(self, code: str) -> Dict[str, Any]:
        """Adquiere un token de acceso usando el código de autorización.
        
        Args:
            code: Código de autorización recibido del flujo OAuth
            
        Returns:
            Diccionario con el token de acceso y otra información
        """
        try:
            result = self.client_instance.acquire_token_by_authorization_code(
                code=code,
                scopes=self.settings.SCOPES,
                redirect_uri=f"{self.settings.FRONTEND_URL}{self.settings.REDIRECT_PATH}"
            )
            
            if "error" in result:
                logger.error(f"Error en acquire_token_by_code: {result.get('error_description')}")
                raise Exception(result.get("error_description"))
                
            return result
        except Exception as e:
            logger.error(f"Error al adquirir token: {e}")
            raise
    
    def get_user_info(self, access_token: str) -> Tuple[str, str]:
        """Obtiene información del usuario desde Microsoft Graph API.
        
        Args:
            access_token: Token de acceso válido
            
        Returns:
            Tupla con (nombre_usuario, correo_usuario)
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
            response.raise_for_status()
            
            profile = response.json()
            logger.debug(f"Perfil obtenido: {profile}")
            
            nombre = profile.get('displayName', 'Usuario')
            correo = profile.get('mail') or profile.get('userPrincipalName', 'sin-correo')
            
            return nombre, correo
        except requests.HTTPError as e:
            logger.error(f"Error HTTP al obtener perfil de usuario: {e.response.text if hasattr(e, 'response') else e}")
            raise
        except Exception as e:
            logger.error(f"Error desconocido al obtener perfil de usuario: {e}")
            raise


# Instancia global del servicio de autenticación
auth_service = AuthService() 