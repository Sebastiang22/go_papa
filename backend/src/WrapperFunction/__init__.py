# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.chat_agent import chat_agent_router
from api.orders import orders_router
from api.inventory_router import inventory_router

from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application startup and shutdown events."""
    print("Aplicación iniciada")
    yield

app = FastAPI(title="TARS Agents Graphs", lifespan=lifespan, root_path="/api")

@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers sin el prefijo /api ya que está en root_path
app.include_router(chat_agent_router, prefix="/agent/chat", tags=["RestaurantsAgents"])
app.include_router(inventory_router, prefix="/inventory/stock", tags=["StockRestaurants"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Montar archivos estáticos (si es necesario)
# app.mount("/", StaticFiles(directory="./dist", html=True), name="static")
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
