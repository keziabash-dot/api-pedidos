"""Camada de API: interface HTTP dos pedidos."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.pedido_repository import PedidoRepository
from app.schemas.pedido import PedidoCreate, PedidoResponse, StatusUpdate
from app.services.pedido_service import (
    PedidoNaoEncontradoError,
    PedidoService,
    TransicaoStatusInvalidaError,
)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def get_service(db: Session = Depends(get_db)) -> PedidoService:
    return PedidoService(PedidoRepository(db))


@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(
    dados: PedidoCreate,
    response: Response,
    service: PedidoService = Depends(get_service),
):
    pedido = service.criar_pedido(dados)
    response.headers["Location"] = f"/pedidos/{pedido.id}"
    return pedido


@router.get("", response_model=list[PedidoResponse])
def listar_pedidos(service: PedidoService = Depends(get_service)):
    return service.listar_pedidos()


@router.get("/{pedido_id}", response_model=PedidoResponse)
def consultar_pedido(pedido_id: int, service: PedidoService = Depends(get_service)):
    try:
        return service.obter_pedido(pedido_id)
    except PedidoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{pedido_id}/status", response_model=PedidoResponse)
def alterar_status(
    pedido_id: int,
    dados: StatusUpdate,
    service: PedidoService = Depends(get_service),
):
    try:
        return service.alterar_status(pedido_id, dados.status)
    except PedidoNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except TransicaoStatusInvalidaError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
