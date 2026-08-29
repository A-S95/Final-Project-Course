from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa de que todos os modelos ORM herdam.

    Mantida à parte de `session.py` para o Alembic conseguir importar
    `Base.metadata` sem também importar o engine/sessão da aplicação.
    """
