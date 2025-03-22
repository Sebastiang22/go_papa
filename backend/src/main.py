# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat_agent import chat_agent_router
from api.orders import orders_router
from api.inventory_router import inventory_router
# from api import auth
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application startup and shutdown events."""
    print("Aplicación iniciada")
    # Aquí podrías inicializar otros servicios o conexiones
    yield
    # Cleanup code (if needed) would go here

app = FastAPI(title="TARS Agents Graphs", lifespan=lifespan)

# Define los orígenes permitidos según donde se encuentre tu frontend.
# En desarrollo podrías usar:
# "http://localhost:3001"
# En producción, por ejemplo, si accedes mediante IP:
# "http://198.244.188.104:3001"
allowed_origins = ["*"]

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
