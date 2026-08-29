from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories import refresh_token_repository


def _make_user(db_session: Session) -> User:
    user = User(email="cleanup@example.com", password_hash="x", name="Teste")
    db_session.add(user)
    db_session.flush()
    return user


def test_delete_expired_removes_only_past_expiry(db_session: Session) -> None:
    user = _make_user(db_session)
    now = datetime.now(UTC)
    expired = RefreshToken(
        user_id=user.id, token_hash="expired", expires_at=now - timedelta(days=1)
    )
    valid = RefreshToken(user_id=user.id, token_hash="valid", expires_at=now + timedelta(days=1))
    db_session.add_all([expired, valid])
    db_session.flush()

    deleted = refresh_token_repository.delete_expired(db_session)

    assert deleted == 1
    remaining = db_session.query(RefreshToken).filter_by(user_id=user.id).all()
    assert [t.token_hash for t in remaining] == ["valid"]


def test_delete_expired_keeps_revoked_tokens_that_have_not_expired_yet(db_session: Session) -> None:
    """Um token revogado por rotação continua a servir para detetar reutilização
    (replay) até ao `expires_at` original — a limpeza não pode apagá-lo mais cedo."""
    user = _make_user(db_session)
    now = datetime.now(UTC)
    revoked_but_not_expired = RefreshToken(
        user_id=user.id, token_hash="revoked", expires_at=now + timedelta(days=1), revoked=True
    )
    db_session.add(revoked_but_not_expired)
    db_session.flush()

    deleted = refresh_token_repository.delete_expired(db_session)

    assert deleted == 0
    assert db_session.query(RefreshToken).filter_by(token_hash="revoked").one_or_none() is not None
