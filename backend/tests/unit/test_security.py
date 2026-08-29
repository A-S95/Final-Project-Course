import uuid

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    password = "correct horse battery staple"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong password", hashed)


def test_access_token_roundtrip() -> None:
    subject = str(uuid.uuid4())
    token = create_access_token(subject)

    payload = decode_access_token(token)

    assert payload["sub"] == subject
    assert payload["type"] == "access"


def test_access_token_rejects_tampering() -> None:
    token = create_access_token(str(uuid.uuid4()))

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token + "tampered")


def test_refresh_token_is_high_entropy_and_hash_is_deterministic() -> None:
    token_a = generate_refresh_token()
    token_b = generate_refresh_token()

    assert token_a != token_b
    assert len(token_a) > 64

    assert hash_refresh_token(token_a) == hash_refresh_token(token_a)
    assert hash_refresh_token(token_a) != hash_refresh_token(token_b)
