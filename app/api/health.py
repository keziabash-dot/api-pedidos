"""Endpoint de saúde (não é funcionalidade de negócio)."""
from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["Saúde"])


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}
