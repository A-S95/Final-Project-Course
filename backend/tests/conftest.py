from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.db.session import engine, get_db
from app.main import app


@pytest.fixture(autouse=True)
def _disable_rate_limiting() -> Iterator[None]:
    """Desliga o rate limiting em todos os testes por omissão.

    O limiter conta pedidos por IP num store em memória partilhado por todo o
    processo de testes; como o `TestClient` usa sempre o mesmo IP fictício, os
    muitos `login`/`register` espalhados pela suite esgotariam o limite real
    (10/minuto) sem isto. `tests/security/test_rate_limiting.py` volta a
    ligar o limiter explicitamente (e limpa o seu storage) para testar o
    comportamento a sério.
    """
    limiter.enabled = False
    yield
    limiter.enabled = False


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Sessão ligada a uma transação que é sempre revertida no fim do teste.

    Corre contra o Postgres real do docker-compose (ver ARCHITECTURE.md —
    decisão de não usar Testcontainers), mas nunca deixa dados persistidos
    entre testes.

    `join_transaction_mode="create_savepoint"`: código de aplicação (ex: os
    routers de auth) chama `db.commit()` a sério. Sem isto, esse commit
    terminaria a transação externa aberta aqui, e os dados do teste ficariam
    de facto gravados na base de dados. Com savepoints, cada `commit()` do
    código sob teste só liberta um SAVEPOINT e abre logo outro — a transação
    externa mantém-se viva até ao `transaction.rollback()` no fim.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """TestClient cuja app usa a `db_session` transacional (acima) em vez de abrir
    a sua própria ligação — assim os pedidos HTTP dos testes também ficam sempre
    revertidos no fim, sem tocar em dados reais.
    """

    def _override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
