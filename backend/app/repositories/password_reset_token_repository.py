import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


def create(
    db: Session, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime
) -> PasswordResetToken:
    token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    db.flush()
    return token


def get_by_hash(db: Session, token_hash: str) -> PasswordResetToken | None:
    return db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )


def mark_used(db: Session, token: PasswordResetToken) -> None:
    token.used_at = datetime.now(UTC)
    db.flush()


def delete_all_for_user(db: Session, user_id: uuid.UUID) -> None:
    """Um novo pedido de recuperação invalida os anteriores — só o link mais
    recente funciona."""
    db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id))
    db.flush()


def delete_expired(db: Session) -> int:
    result = db.execute(
        delete(PasswordResetToken).where(PasswordResetToken.expires_at < datetime.now(UTC))
    )
    db.flush()
    return result.rowcount
