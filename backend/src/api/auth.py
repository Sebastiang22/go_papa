from fastapi import Response, Request, APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from msal import ConfidentialClientApplication
import requests
import json
import os

from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
# REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

client_instance = ConfidentialClientApplication(
    client_id = CLIENT_ID,
    client_credential = CLIENT_SECRET,
    authority = AUTHORITY
)

@router.get("/login")
def login(request: Request):
    prompt = request.query_params.get('prompt', None)
    if prompt:
        redirect_uri = client_instance.get_authorization_request_url(SCOPES, prompt='login')
    else:
        redirect_uri = client_instance.get_authorization_request_url(SCOPES)
    return RedirectResponse(redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(content={"error": "Authorization code not found"}, status_code=400)
    
    request_token = client_instance.acquire_token_by_authorization_code(
        code = code,
        scopes = SCOPES
    )
    if "access_token" in request_token:
        try:
            nombre, correo = requestProfile(request_token["access_token"])
        except requests.HTTPError:
            raise HTTPException(status_code=400, detail="Failed to fetch profile information")
        
        query_params = urlencode({ "name": nombre, "email": correo })
        response = RedirectResponse(url=f"https://aw-gopapa-ancpabaybmhxbuc9.westus2-01.azurewebsites.net/?{query_params}")
        # response = RedirectResponse(url=f"http://localhost:5173/?{query_params}")
        # import pdb
        # pdb.set_trace()
        return response
    else:
        raise HTTPException(status_code=400, detail="Token acquisition failed")#return JSONResponse(content={"error": "Token acquisition failed"}, status_code=400)


def requestProfile(token):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    response.raise_for_status()
    profile = response.json()
    print(profile)
    nombre = profile['displayName']
    correo = profile['mail']
    return nombre, correo
    
@router.get("/test")
async def root():
    return JSONResponse(content={"message": "ok"}, status_code=200)
