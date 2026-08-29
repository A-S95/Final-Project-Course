from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# `pool_pre_ping`: testa cada ligação com um SELECT trivial antes de a usar, para
# não rebentar com "connection already closed" se o Postgres reiniciar entretanto
# (ex: `docker compose restart postgres`) e uma ligação do pool ficar velha.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI: uma sessão por pedido, fechada no fim."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
