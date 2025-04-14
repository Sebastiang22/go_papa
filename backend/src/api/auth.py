from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from msal import ConfidentialClientApplication
import requests
import json
import os
import jwt
from datetime import datetime, timedelta

from urllib.parse import urlencode

from core.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
# Actualizar REDIRECT_URI para usar el backend desplegado
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://af-gopapa.azurewebsites.net/auth/callback")
# Actualizar FRONTEND_URL para usar el frontend desplegado
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://yellow-plant-06f40fa0f.6.azurestaticapps.net")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]
JWT_SECRET = os.getenv("JWT_SECRET", "mi_secreto_super_seguro_para_jwt_tokens")

client_instance = ConfidentialClientApplication(
    client_id = CLIENT_ID,
    client_credential = CLIENT_SECRET,
    authority = AUTHORITY
)

@router.get("/login")
def login(request: Request):
    # Crear URL de autorización con REDIRECT_URI
    auth_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "response_mode": "query"
    }
    
    # Añadir prompt=login si se solicita
    prompt = request.query_params.get('prompt', None)
    if prompt:
        auth_params["prompt"] = "login"
    
    # Construir URL completa
    auth_url = f"{AUTHORITY}/oauth2/v2.0/authorize?{urlencode(auth_params)}"
    return RedirectResponse(auth_url)

def create_jwt_token(user_data):
    """Crear un token JWT con información del usuario"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": user_data["email"],
        "name": user_data["name"],
        "email": user_data["email"],
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

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
    
    # Adquirir token con el código recibido
    request_token = client_instance.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    if "access_token" in request_token:
        try:
            # Obtener perfil del usuario
            nombre, correo = requestProfile(request_token["access_token"])
            
            # Crear token JWT
            user_data = {"name": nombre, "email": correo}
            token = create_jwt_token(user_data)
            
            # Crear URL de redirección con el token
            redirect_url = f"{FRONTEND_URL}?token={token}"
            
            # Crear respuesta con cookie y redirección
            response = RedirectResponse(url=redirect_url)
            response.set_cookie(
                key="auth_token", 
                value=token,
                httponly=True,
                max_age=86400,  # 24 horas
                samesite="lax",
                secure=True  # Cambiado a True para HTTPS en producción
            )
            
            return response
        except requests.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch profile information: {str(e)}")
    else:
        error_msg = request_token.get("error_description", "Token acquisition failed")
        raise HTTPException(status_code=400, detail=error_msg)

def requestProfile(token):
    """Obtener datos del perfil desde Microsoft Graph API"""
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    response.raise_for_status()
    profile = response.json()
    
    nombre = profile.get('displayName', 'Usuario')
    correo = profile.get('mail') or profile.get('userPrincipalName', 'sin-correo@example.com')
    
    return nombre, correo

@router.get("/verify-token")
async def verify_token(request: Request):
    """Verificar validez del token de autenticación"""
    token = request.cookies.get("auth_token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        return JSONResponse(content={"isValid": False, "error": "No token provided"}, status_code=401)
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return JSONResponse(content={
            "isValid": True,
            "user": {
                "name": payload.get("name"),
                "email": payload.get("sub")
            }
        })
    except jwt.ExpiredSignatureError:
        return JSONResponse(content={"isValid": False, "error": "Token expired"}, status_code=401)
    except jwt.InvalidTokenError:
        return JSONResponse(content={"isValid": False, "error": "Invalid token"}, status_code=401)

@router.get("/logout")
async def logout():
    """Cerrar sesión del usuario"""
    response = RedirectResponse(url=f"{FRONTEND_URL}")
    response.delete_cookie(key="auth_token")
    return response

@router.get("/test")
async def root():
    return JSONResponse(content={"message": "Auth service is working"}, status_code=200)
