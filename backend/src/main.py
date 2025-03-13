# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat_agent import chat_agent_router
from api.orders import orders_router
from api.inventory_router import inventory_router
# from api import auth
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="TARS Agents Graphs")

# Define los orígenes permitidos según donde se encuentre tu frontend.
# En desarrollo podrías usar:
# "http://localhost:3001"
# En producción, por ejemplo, si accedes mediante IP:
# "http://198.244.188.104:3001"
allowed_origins = [
    "http://localhost:3001",
    "http://198.244.188.104:3001",
]

# Configura CORS para permitir peticiones solo desde los orígenes especificados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(chat_agent_router, prefix="/api/agent/chat", tags=["RestaurantsAgents"])
app.include_router(inventory_router, prefix="/api/inventory/stock", tags=["StockRestaurants"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Montar archivos estáticos (si es necesario)
# app.mount("/", StaticFiles(directory="./dist", html=True), name="static")
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    """
    Se llama una sola vez al iniciar la app.
    Puedes inicializar variables globales aquí si fuera necesario
    o delegar a un módulo de dependencias.
    """
    print("Aplicación iniciada")
    # Aquí podrías inicializar otros servicios o conexiones
