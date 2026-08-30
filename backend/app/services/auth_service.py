from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.repositories import refresh_token_repository, user_repository


def _issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(str(user.id))
    refresh_token = generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    refresh_token_repository.create(
        db, user_id=user.id, token_hash=hash_refresh_token(refresh_token), expires_at=expires_at
    )
    return access_token, refresh_token


def register_user(db: Session, *, email: str, password: str, name: str) -> tuple[User, str, str]:
    if user_repository.get_by_email(db, email) is not None:
        raise EmailAlreadyRegisteredError(email)
    user = user_repository.create(db, email=email, password_hash=hash_password(password), name=name)
    access_token, refresh_token = _issue_tokens(db, user)
    return user, access_token, refresh_token


def authenticate(db: Session, *, email: str, password: str) -> tuple[User, str, str]:
    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError
    access_token, refresh_token = _issue_tokens(db, user)
    return user, access_token, refresh_token


def refresh_tokens(db: Session, *, refresh_token: str) -> tuple[User, str, str]:
    stored = refresh_token_repository.get_by_hash(db, hash_refresh_token(refresh_token))
    if stored is None or stored.expires_at < datetime.now(UTC):
        raise InvalidRefreshTokenError

    if stored.revoked:
        # Token já rodado a ser reutilizado: assume-se roubo, revoga toda a família.
        refresh_token_repository.revoke_all_for_user(db, stored.user_id)
        raise InvalidRefreshTokenError

    refresh_token_repository.revoke(db, stored)  # rotação: impede reutilização (replay)

    user = user_repository.get_by_id(db, stored.user_id)
    if user is None:
        raise InvalidRefreshTokenError

    access_token, new_refresh_token = _issue_tokens(db, user)
    return user, access_token, new_refresh_token


def logout(db: Session, *, refresh_token: str) -> None:
    stored = refresh_token_repository.get_by_hash(db, hash_refresh_token(refresh_token))
    if stored is not None and not stored.revoked:
        refresh_token_repository.revoke(db, stored)
