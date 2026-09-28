"""Camada de lógica: aplica regras, calcula valores e coordena operações."""
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from app.models.pedido import Pedido, StatusPedido
from app.repositories.pedido_repository import PedidoRepository
from app.schemas.pedido import PedidoCreate

ID_MAXIMO = 2_147_483_647  # limite da coluna INTEGER do PostgreSQL

# Regras de transição de status:
#   CRIADO     -> CONFIRMADO ou CANCELADO
#   CONFIRMADO -> CANCELADO
#   CANCELADO  -> (estado final)
TRANSICOES_PERMITIDAS: dict[StatusPedido, set[StatusPedido]] = {
    StatusPedido.CRIADO: {StatusPedido.CONFIRMADO, StatusPedido.CANCELADO},
    StatusPedido.CONFIRMADO: {StatusPedido.CANCELADO},
    StatusPedido.CANCELADO: set(),
}


class PedidoNaoEncontradoError(Exception):
    def __init__(self, pedido_id: int):
        super().__init__(f"Pedido {pedido_id} não encontrado.")
        self.pedido_id = pedido_id


class TransicaoStatusInvalidaError(Exception):
    def __init__(self, atual: StatusPedido, novo: StatusPedido):
        super().__init__(
            f"Não é permitido alterar o status de {atual.value} para {novo.value}."
        )


class PedidoService:
    def __init__(self, repository: PedidoRepository):
        self.repository = repository

    @staticmethod
    def calcular_valor_total(quantidade: int, valor_unitario: Decimal) -> Decimal:
        total = Decimal(quantidade) * valor_unitario
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def criar_pedido(self, dados: PedidoCreate) -> Pedido:
        pedido = Pedido(
            cliente=dados.cliente,
            produto=dados.produto,
            quantidade=dados.quantidade,
            valor_unitario=dados.valor_unitario,
            valor_total=self.calcular_valor_total(dados.quantidade, dados.valor_unitario),
            status=StatusPedido.CRIADO,  # status inicial definido pela aplicação
            data_criacao=datetime.now(timezone.utc),
        )
        return self.repository.criar(pedido)

    def obter_pedido(self, pedido_id: int) -> Pedido:
        if not 1 <= pedido_id <= ID_MAXIMO:
            raise PedidoNaoEncontradoError(pedido_id)
        pedido = self.repository.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNaoEncontradoError(pedido_id)
        return pedido

    def listar_pedidos(self) -> list[Pedido]:
        return self.repository.listar()

    def alterar_status(self, pedido_id: int, novo_status: StatusPedido) -> Pedido:
        pedido = self.obter_pedido(pedido_id)
        if pedido.status == novo_status:
            return pedido  # operação idempotente
        if novo_status not in TRANSICOES_PERMITIDAS[pedido.status]:
            raise TransicaoStatusInvalidaError(pedido.status, novo_status)
        return self.repository.atualizar_status(pedido, novo_status)
