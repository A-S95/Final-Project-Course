import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(subject: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def generate_refresh_token() -> str:
    """Token opaco de alta entropia — não é um JWT, só um segredo aleatório."""
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    """SHA-256, não bcrypt: estes tokens (refresh, reset de password) já são
    aleatórios de alta entropia, ao contrário de uma password escolhida por um
    humano — não há força bruta/dicionário a mitigar, por isso não se justifica o
    custo de um hash lento. Guardar em claro é que nunca seria aceitável (um leak
    da tabela daria acesso direto).
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_refresh_token(token: str) -> str:
    return hash_token(token)
