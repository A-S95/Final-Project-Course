"""Testes do rate limiting em /login e /register (proteção contra força bruta).

O resto da suite corre com o limiter desligado (ver `tests/conftest.py` —
`_disable_rate_limiting`, autouse) porque o `TestClient` usa sempre o mesmo IP
fictício e a suite faz muitos mais que 10 pedidos de login/registo no total.
Este ficheiro liga o limiter só para si e limpa o seu storage em memória antes
e depois, para não interferir com o resto da suite nem com os seus próprios
testes entre si.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.rate_limit import limiter

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

# Tem de corresponder ao limite configurado em app/api/v1/auth.py.
LIMIT_PER_MINUTE = 10


@pytest.fixture(autouse=True)
def _enable_rate_limiting() -> None:
    limiter.reset()
    limiter.enabled = True
    yield
    limiter.enabled = False
    limiter.reset()


def test_login_is_rate_limited_after_too_many_attempts(client: TestClient) -> None:
    responses = [
        client.post(LOGIN_URL, json={"email": "ataque@example.com", "password": "errada"})
        for _ in range(LIMIT_PER_MINUTE + 1)
    ]

    # As primeiras LIMIT_PER_MINUTE tentativas seguem o fluxo normal (401,
    # credenciais inválidas) — só a que excede o limite é bloqueada.
    assert all(r.status_code == 401 for r in responses[:LIMIT_PER_MINUTE])
    blocked = responses[LIMIT_PER_MINUTE]
    assert blocked.status_code == 429
    assert "detail" in blocked.json()


def test_register_is_rate_limited_after_too_many_attempts(client: TestClient) -> None:
    responses = [
        client.post(
            REGISTER_URL,
            json={
                "email": f"utilizador{i}@example.com",
                "password": "correct horse battery staple",
                "name": "Teste",
            },
        )
        for i in range(LIMIT_PER_MINUTE + 1)
    ]

    assert all(r.status_code == 201 for r in responses[:LIMIT_PER_MINUTE])
    blocked = responses[LIMIT_PER_MINUTE]
    assert blocked.status_code == 429


def test_rate_limit_is_scoped_per_endpoint(client: TestClient) -> None:
    """Esgotar o limite do /login não deve afetar o /register — cada rota tem
    o seu próprio contador (a chave inclui o path, não só o IP)."""
    for _ in range(LIMIT_PER_MINUTE + 1):
        client.post(LOGIN_URL, json={"email": "ataque@example.com", "password": "errada"})

    response = client.post(
        REGISTER_URL,
        json={
            "email": "outro@example.com",
            "password": "correct horse battery staple",
            "name": "Teste",
        },
    )

    assert response.status_code == 201
