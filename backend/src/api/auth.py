from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import logging
from urllib.parse import urlencode

from core.auth_service import auth_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/login")
def login(request: Request):
    """Inicia el flujo de autenticación con Microsoft Entra ID.
    
    Redirecciona al usuario a la página de inicio de sesión de Microsoft.
    
    Args:
        request: Solicitud HTTP con posibles parámetros de consulta
        
    Returns:
        Redirección a la página de inicio de sesión de Microsoft
    """
    try:
        prompt = request.query_params.get('prompt')
        redirect_uri = auth_service.get_auth_url(prompt)
        logger.info("Iniciando flujo de autenticación Microsoft Entra ID")
        return RedirectResponse(redirect_uri)
    except Exception as e:
        logger.error(f"Error en el inicio de sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error de autenticación: {str(e)}")


@router.get("/callback")
async def auth_callback(request: Request):
    """Maneja la respuesta de autenticación de Microsoft Entra ID.
    
    Esta ruta recibe el código de autorización y lo intercambia por un token de acceso.
    Luego obtiene información del usuario y redirecciona al frontend con esos datos.
    
    Args:
        request: Solicitud HTTP con el código de autorización
        
    Returns:
        Redirección al frontend con datos del usuario autenticado
    """
    code = request.query_params.get("code")
    if not code:
        logger.warning("Callback sin código de autorización")
        return JSONResponse(content={"error": "Código de autorización no encontrado"}, status_code=400)
    
    try:
        # Obtener token usando el código de autorización
        token_result = auth_service.acquire_token_by_code(code)
        
        if "access_token" not in token_result:
            logger.error(f"Error en adquisición de token: {token_result.get('error_description', 'Error desconocido')}")
            raise HTTPException(
                status_code=400, 
                detail=f"Error al obtener token: {token_result.get('error_description', 'Error desconocido')}"
            )
        
        # Obtener información del usuario
        nombre, correo = auth_service.get_user_info(token_result["access_token"])
        
        # Crear parámetros para la redirección
        query_params = urlencode({
            "name": nombre,
            "email": correo,
            "token": token_result["access_token"],
            "expires_in": token_result.get("expires_in", 3600)
        })
        
        # Redireccionar al frontend con la información
        logger.info(f"Autenticación exitosa para usuario: {correo}")
        return RedirectResponse(url=f"{auth_service.settings.FRONTEND_URL}/?{query_params}")
    
    except Exception as e:
        logger.error(f"Error en callback de autenticación: {e}")
        raise HTTPException(status_code=500, detail=f"Error de autenticación: {str(e)}")


@router.post("/validate-token")
async def validate_token(request: Request):
    """Valida un token de acceso y retorna información del usuario.
    
    Args:
        request: Solicitud HTTP con el token a validar en el cuerpo
        
    Returns:
        Información del usuario si el token es válido
    """
    try:
        data = await request.json()
        token = data.get("token")
        
        if not token:
            return JSONResponse(
                content={"valid": False, "error": "No se proporcionó token"}, 
                status_code=400
            )
        
        # Verificar el token obteniendo información del usuario
        nombre, correo = auth_service.get_user_info(token)
        
        return JSONResponse(content={
            "valid": True,
            "name": nombre,
            "email": correo
        })
    except Exception as e:
        logger.warning(f"Validación de token fallida: {e}")
        return JSONResponse(
            content={"valid": False, "error": str(e)},
            status_code=401
        )


@router.get("/test")
async def test_auth():
    """Endpoint de prueba para verificar que el router de autenticación está funcionando."""
    return JSONResponse(content={"message": "Módulo de autenticación funcionando correctamente"}, status_code=200)
