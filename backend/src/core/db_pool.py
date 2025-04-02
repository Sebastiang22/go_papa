import asyncio
import logging
from typing import Optional, Dict, Any

import aiomysql
from aiomysql import Pool

from core.config import settings

class DBConnectionPool:
    """
    Implementación singleton de un pool de conexiones a MySQL.
    Permite que todas las clases compartan el mismo pool para evitar
    el error "Too many connections".
    """
    _instance: Optional['DBConnectionPool'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnectionPool, cls).__new__(cls)
            cls._instance.pool = None
            cls._instance._pool_initialized = False
        return cls._instance
    
    async def get_pool(self) -> Pool:
        """
        Obtiene el pool de conexiones, creándolo si no existe.
        
        Returns:
            Pool: Pool de conexiones a MySQL
        """
        async with self._lock:
            if not self._pool_initialized:
                try:
                    logging.info("Inicializando pool de conexiones a MySQL...")
                    self.pool = await aiomysql.create_pool(
                        host=settings.db_host,
                        user=settings.db_user,
                        password=settings.db_password,
                        db=settings.db_database,
                        autocommit=False,
                        maxsize=30,  # Aumentado de 25 a 30 para manejar más conexiones
                        minsize=10,  # Aumentado de 5 a 10 para tener más conexiones pre-calentadas
                        pool_recycle=1200,  # Reducido de 1800 a 1200 para reciclar conexiones cada 20 minutos
                        echo=True,  # Activar logging de consultas SQL para debugging
                        charset='utf8mb4',  # Soporte para caracteres Unicode completo
                        connect_timeout=10.0  # Timeout para conexiones
                    )
                    self._pool_initialized = True
                    logging.info("Pool de conexiones MySQL creado correctamente")
                except Exception as err:
                    logging.error(f"Error al crear el pool de conexiones: {err}")
                    self._pool_initialized = False
                    raise
            return self.pool
    
    async def close(self):
        """Cierra el pool de conexiones."""
        async with self._lock:
            if self.pool and self._pool_initialized:
                self.pool.close()
                await self.pool.wait_closed()
                self._pool_initialized = False
                logging.info("Pool de conexiones cerrado correctamente")
    
    async def __aenter__(self):
        await self.get_pool()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  # No cerramos el pool aquí, el cierre debe ser explícito 