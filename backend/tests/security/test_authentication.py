"""Autenticação: só um access token JWT válido (assinatura certa, não expirado,
`sub` = utilizador existente) dá acesso. Qualquer outra coisa -> 401 limpo,
nunca 500.
"""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.api.helpers import register_and_get_headers

PROTECTED_ENDPOINTS = [
    ("GET", "/api/v1/users/me"),
    ("GET", "/api/v1/accounts"),
    ("GET", "/api/v1/categories"),
    ("GET", "/api/v1/transactions"),
    ("GET", "/api/v1/budgets"),
    ("GET", "/api/v1/goals"),
    ("GET", "/api/v1/recurring-expenses"),
    ("GET", "/api/v1/dashboard"),
    ("GET", "/api/v1/insights"),
    ("GET", "/api/v1/analytics/monthly-comparison"),
    ("GET", "/api/v1/analytics/monthly-trend"),
    ("GET", "/api/v1/households/me"),
    ("GET", "/api/v1/households/invites"),
    ("POST", "/api/v1/recurring-expenses/generate"),
]


def _token(payload: dict, *, key: str | None = None, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, key or settings.secret_key, algorithm=algorithm)


def _valid_payload(sub: str | None = None) -> dict:
    now = datetime.now(UTC)
    return {
        "sub": sub or str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "type": "access",
    }


def test_all_protected_endpoints_require_a_token(client: TestClient) -> None:
    for method, path in PROTECTED_ENDPOINTS:
        response = client.request(method, path)
        assert response.status_code == 401, (method, path, response.status_code)


def test_malformed_authorization_headers_are_rejected(client: TestClient) -> None:
    for value in ["", "Bearer", "Bearer ", "Bearer not-a-jwt", "Basic dXNlcjpwYXNz", "garbage",
                  "Bearer a.b.c", "Bearer  "]:
        response = client.get("/api/v1/users/me", headers={"Authorization": value})
        assert response.status_code == 401, (value, response.status_code)


def test_token_signed_with_the_wrong_secret_is_rejected(client: TestClient) -> None:
    forged = _token(_valid_payload(), key="0" * 64)  # chave errada, comprimento válido
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {forged}"}
    )
    assert response.status_code == 401


def test_unsigned_alg_none_token_is_rejected(client: TestClient) -> None:
    # Ataque clássico "alg: none" — PyJWT recusa por defeito (algorithms=["HS256"]).
    unsigned = jwt.encode(_valid_payload(), key=None, algorithm="none")
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {unsigned}"}
    )
    assert response.status_code == 401


def test_expired_token_is_rejected(client: TestClient) -> None:
    now = datetime.now(UTC)
    expired = _token(
        {"sub": str(uuid.uuid4()), "iat": now - timedelta(hours=2),
         "exp": now - timedelta(hours=1), "type": "access"}
    )
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {expired}"}
    )
    assert response.status_code == 401


def test_valid_signature_but_unknown_user_is_rejected(client: TestClient) -> None:
    # Assinatura certa mas o `sub` não corresponde a nenhum utilizador.
    token = _token(_valid_payload(sub=str(uuid.uuid4())))
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_valid_signature_but_malformed_sub_is_rejected_cleanly(client: TestClient) -> None:
    # `sub` não é um UUID / está em falta — tem de dar 401, nunca 500 (ver deps.py).
    for bad_sub in ["not-a-uuid", "12345", ""]:
        token = _token(_valid_payload(sub=bad_sub))
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401, (bad_sub, response.status_code)

    no_sub = _token({"iat": datetime.now(UTC), "exp": datetime.now(UTC) + timedelta(minutes=5)})
    assert client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {no_sub}"}
    ).status_code == 401


def test_a_genuine_token_still_works(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    assert client.get("/api/v1/users/me", headers=headers).status_code == 200
