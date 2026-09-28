"""Schemas de entrada e saída da API (validação da estrutura recebida)."""
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, StringConstraints

from app.models.pedido import StatusPedido

TextoObrigatorio = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
]
# Valores monetários são armazenados como Decimal, mas saem como número no JSON.
Dinheiro = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class PedidoCreate(BaseModel):
    """Entrada do POST /pedidos. valor_total e status NÃO são aceitos do cliente."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "cliente": "Maria Silva",
                "produto": "Teclado mecânico",
                "quantidade": 2,
                "valor_unitario": 249.90,
            }
        },
    )

    cliente: TextoObrigatorio
    produto: TextoObrigatorio
    quantidade: int = Field(gt=0, le=1_000_000)
    valor_unitario: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente: str
    produto: str
    quantidade: int
    valor_unitario: Dinheiro
    valor_total: Dinheiro
    status: StatusPedido
    data_criacao: datetime


class StatusUpdate(BaseModel):
    """Entrada do PATCH /pedidos/{id}/status."""

    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"example": {"status": "CONFIRMADO"}}
    )

    status: StatusPedido
