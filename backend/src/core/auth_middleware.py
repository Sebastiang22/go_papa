from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import time
from typing import List, Callable, Optional
import jwt
from jwt.exceptions import PyJWTError

logger = logging.getLogger(__name__)

# Rutas que están exentas de autenticación
EXCLUDED_ROUTES: List[str] = [
    "/auth/login",
    "/auth/callback",
    "/auth/test",
    "/auth/validate-token",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/orders/today",
    "/agent/chat/message",
    "/orders/update_state"  # Añadido temporalmente para permitir pruebas sin autenticación
]

# Función para verificar si una ruta está excluida de autenticación
def is_excluded_route(path: str) -> bool:
    """Determina si una ruta está excluida de autenticación."""
    return any(path.startswith(route) for route in EXCLUDED_ROUTES)

# Clase para validar tokens y extraer su información
class TokenValidator:
    """Clase para validar tokens de Microsoft Entra ID."""
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decodifica un token JWT sin verificación criptográfica.
        
        Esta función extrae información básica del token pero NO valida
        su autenticidad. La validación real se hace al consultar Microsoft Graph.
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Diccionario con los datos del token o None si es inválido
        """
        try:
            # Decodificar sin verificar firma para obtener información básica
            # Esto es solo para extraer datos, la validación real se hace con Microsoft Graph
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except PyJWTError as e:
            logger.warning(f"Error al decodificar token: {e}")
            return None

# Middleware de autenticación para FastAPI
async def auth_middleware(request: Request, call_next):
    """Middleware que verifica la autenticación de las solicitudes.
    
    Verifica que las solicitudes a rutas protegidas incluyan un token válido.
    Las rutas excluidas (definidas en EXCLUDED_ROUTES) no requieren autenticación.
    
    Args:
        request: Objeto Request de FastAPI
        call_next: Función para llamar al siguiente middleware o endpoint
        
    Returns:
        Respuesta HTTP apropiada
    """
    start_time = time.time()
    
    # Verificar si la ruta está excluida de autenticación
    if is_excluded_route(request.url.path):
        return await call_next(request)
    
    # Verificar la presencia del encabezado de autorización
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning(f"Acceso denegado a {request.url.path}: falta token de autorización")
        return JSONResponse(
            status_code=401,
            content={"detail": "Se requiere autenticación"}
        )
    
    # Extraer y validar el token
    token = auth_header.replace("Bearer ", "")
    token_data = TokenValidator.decode_token(token)
    
    if not token_data:
        logger.warning(f"Acceso denegado a {request.url.path}: token inválido")
        return JSONResponse(
            status_code=401,
            content={"detail": "Token inválido o malformado"}
        )
    
    # Verificar expiración del token
    current_time = int(time.time())
    expiry_time = token_data.get("exp", 0)
    
    if current_time > expiry_time:
        logger.warning(f"Acceso denegado a {request.url.path}: token expirado")
        return JSONResponse(
            status_code=401,
            content={"detail": "Token expirado"}
        )
    
    # Continuar con la solicitud si el token parece válido
    response = await call_next(request)
    
    # Registrar tiempo de procesamiento
    process_time = time.time() - start_time
    logger.debug(f"Procesado en {process_time:.4f} seg: {request.method} {request.url.path}")
    
    return response 