import logging
import re
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken
from tests.api.helpers import register

REQUEST_URL = "/api/v1/auth/password-reset/request"
CONFIRM_URL = "/api/v1/auth/password-reset/confirm"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
OLD_PASSWORD = "correct horse battery staple"
NEW_PASSWORD = "uma password completamente nova"


def _reset_token_from_logs(caplog: pytest.LogCaptureFixture) -> str:
    for record in caplog.records:
        match = re.search(r"redefinir-password\?token=([A-Za-z0-9_-]+)", record.getMessage())
        if match:
            return match.group(1)
    raise AssertionError("Nenhum email de recuperação foi registado (modo consola).")


def _request_reset(client: TestClient, caplog: pytest.LogCaptureFixture, email: str) -> str:
    with caplog.at_level(logging.INFO):
        assert client.post(REQUEST_URL, json={"email": email}).status_code == 202
    return _reset_token_from_logs(caplog)


def _confirm(client: TestClient, token: str, password: str = NEW_PASSWORD) -> int:
    return client.post(CONFIRM_URL, json={"token": token, "password": password}).status_code


def _login(client: TestClient, email: str, password: str) -> int:
    return client.post(LOGIN_URL, json={"email": email, "password": password}).status_code


def test_request_for_unknown_email_still_returns_202(client: TestClient) -> None:
    response = client.post(REQUEST_URL, json={"email": "ninguem@example.com"})
    assert response.status_code == 202
    # Mensagem genérica — não confirma nem nega que a conta existe.
    assert "Se existir uma conta" in response.json()["detail"]


def test_full_reset_flow_changes_the_password(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    register(client, email="reset@example.com")
    token = _request_reset(client, caplog, "reset@example.com")

    assert _confirm(client, token) == 200
    assert _login(client, "reset@example.com", OLD_PASSWORD) == 401
    assert _login(client, "reset@example.com", NEW_PASSWORD) == 200


def test_reset_revokes_existing_sessions(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    register(client, email="reset2@example.com")  # deixa um refresh cookie na sessão do client
    token = _request_reset(client, caplog, "reset2@example.com")
    _confirm(client, token)

    # O refresh token de antes da reposição já não vale.
    assert client.post(REFRESH_URL).status_code == 401


def test_token_cannot_be_reused(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    register(client, email="reset3@example.com")
    token = _request_reset(client, caplog, "reset3@example.com")

    assert _confirm(client, token) == 200
    assert _confirm(client, token, "outra password diferente") == 400


def test_a_new_request_invalidates_the_previous_link(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    register(client, email="reset4@example.com")
    first_token = _request_reset(client, caplog, "reset4@example.com")
    caplog.clear()
    second_token = _request_reset(client, caplog, "reset4@example.com")

    assert first_token != second_token
    assert _confirm(client, first_token) == 400
    assert _confirm(client, second_token) == 200


def test_expired_token_is_rejected(
    client: TestClient, db_session: Session, caplog: pytest.LogCaptureFixture
) -> None:
    user_id = uuid.UUID(register(client, email="reset5@example.com")["user"]["id"])
    token = _request_reset(client, caplog, "reset5@example.com")

    # Filtra pelo user — a tabela pode ter tokens de sessões manuais.
    stored = db_session.scalars(
        select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
    ).one()
    stored.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db_session.flush()

    assert _confirm(client, token) == 400


def test_confirm_with_garbage_token_returns_400(client: TestClient) -> None:
    assert _confirm(client, "nao-e-um-token") == 400


def test_confirm_rejects_short_password(client: TestClient) -> None:
    assert _confirm(client, "qualquer", "curta") == 422


def test_reset_endpoints_do_not_require_authentication(client: TestClient) -> None:
    # Sem header Authorization — é esse o objetivo de todo o fluxo.
    assert client.post(REQUEST_URL, json={"email": "x@example.com"}).status_code == 202
    assert _confirm(client, "x") == 400
