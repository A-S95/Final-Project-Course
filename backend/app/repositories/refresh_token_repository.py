import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create(
    db: Session, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime
) -> RefreshToken:
    token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    db.flush()
    return token


def get_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    return db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))


def revoke(db: Session, token: RefreshToken) -> None:
    token.revoked = True
    token.revoked_at = datetime.now(UTC)
    db.flush()


def revoke_all_for_user(db: Session, user_id: uuid.UUID) -> None:
    """Revoga todos os refresh tokens ativos do utilizador de uma vez — usado como
    resposta a uma deteção de reutilização de token (possível roubo)."""
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True, revoked_at=datetime.now(UTC))
    )
    db.flush()


def delete_expired(db: Session) -> int:
    """Apaga tokens cujo `expires_at` já passou — chamado periodicamente para a
    tabela não crescer indefinidamente (ver tarefa de fundo em `main.py`).

    Filtra só por `expires_at`, nunca por `revoked`: um token revogado por
    rotação mantém o `expires_at` original e continua a servir para detetar
    reutilização (replay) até essa data — apagá-lo mais cedo abriria uma
    janela onde um token roubado reaparece como "não encontrado" em vez de
    "revogado", perdendo a resposta de revogar toda a família de tokens.
    """
    result = db.execute(delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC)))
    db.flush()
    return result.rowcount
