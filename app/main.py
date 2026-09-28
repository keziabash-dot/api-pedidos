"""Inicialização do FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import health, pedidos
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API de Pedidos",
    description="Trabalho 1 - Desenvolvimento de Sistemas Distribuídos (UNIP)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(pedidos.router)
