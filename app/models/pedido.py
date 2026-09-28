"""Modelo persistente do Pedido (tabela 'pedidos')."""
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StatusPedido(str, enum.Enum):
    CRIADO = "CRIADO"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cliente: Mapped[str] = mapped_column(String(255), nullable=False)
    produto: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    status: Mapped[StatusPedido] = mapped_column(
        SAEnum(StatusPedido, name="status_pedido", native_enum=False, length=20),
        nullable=False,
        default=StatusPedido.CRIADO,
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
