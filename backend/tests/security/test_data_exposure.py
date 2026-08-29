"""Não vazar segredos: passwords/hashes nunca saem nas respostas, o refresh token
é guardado como hash (nunca em claro), o cookie de refresh tem as flags certas, e
os erros não distinguem "email não existe" de "password errada".
"""

import json

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from tests.api.helpers import register_and_get_headers

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


def _contains_key(obj: object, key: str) -> bool:
    if isinstance(obj, dict):
        return key in obj or any(_contains_key(v, key) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_key(v, key) for v in obj)
    return False


def test_register_response_never_contains_password_fields(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": "secrets@example.com", "password": "correct horse battery staple",
              "name": "Sec"},
    )
    assert response.status_code == 201
    body = response.json()
    for forbidden in ("password", "password_hash"):
        assert not _contains_key(body, forbidden)
    assert "$2b$" not in response.text  # nenhum hash bcrypt


def test_users_me_never_leaks_the_hash(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert not _contains_key(response.json(), "password_hash")
    assert "$2b$" not in response.text


def test_refresh_token_is_stored_hashed_not_in_plaintext(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": "rt@example.com", "password": "correct horse battery staple",
              "name": "RT"},
    )
    raw_cookie = response.cookies.get("refresh_token")
    assert raw_cookie is not None

    stored = db_session.scalars(select(RefreshToken)).all()
    assert len(stored) == 1
    assert stored[0].token_hash != raw_cookie  # não está em claro
    assert len(stored[0].token_hash) == 64  # SHA-256 hex
    # E o valor em claro não aparece em lado nenhum da linha.
    assert raw_cookie not in json.dumps(
        {c.name: str(getattr(stored[0], c.name)) for c in RefreshToken.__table__.columns}
    )


def test_refresh_cookie_has_hardened_flags(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": "cookie@example.com", "password": "correct horse battery staple",
              "name": "Cookie"},
    )
    set_cookie = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/api/v1/auth" in set_cookie  # não é enviado nos outros pedidos
    assert "Max-Age=" in set_cookie


def test_login_error_does_not_reveal_whether_the_email_exists(client: TestClient) -> None:
    register_and_get_headers(client, email="known@example.com")

    wrong_password = client.post(
        LOGIN_URL, json={"email": "known@example.com", "password": "wrong-password"}
    )
    unknown_email = client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "wrong-password"}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()  # mensagem idêntica


def test_error_responses_do_not_leak_internals(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    response = client.get(
        "/api/v1/accounts/00000000-0000-0000-0000-000000000000", headers=headers
    )
    # 404 ou 405 (rota não existe para GET /{id}) — nunca uma stack trace.
    assert response.status_code in (404, 405)
    assert "Traceback" not in response.text
    assert "sqlalchemy" not in response.text.lower()
