"""Configuração da conexão com o PostgreSQL.

Nenhum endereço, porta, usuário ou senha fica fixo no código:
tudo vem da variável de ambiente DATABASE_URL.
"""
import logging
import os
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

logger = logging.getLogger("uvicorn.error")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("A variável de ambiente DATABASE_URL não foi definida.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependência do FastAPI: abre uma sessão por requisição e a fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(tentativas: int = 15, intervalo: float = 2.0) -> None:
    """Cria as tabelas, aguardando o banco ficar disponível."""
    import app.models  # noqa: F401  (registra os modelos no metadata)

    for tentativa in range(1, tentativas + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Banco de dados pronto.")
            return
        except OperationalError as exc:
            logger.warning(
                "Banco indisponível (tentativa %d/%d): %s", tentativa, tentativas, exc.orig
            )
            time.sleep(intervalo)
    raise RuntimeError("Não foi possível conectar ao banco de dados.")
