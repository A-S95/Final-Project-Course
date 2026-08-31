import pytest
from fastapi.testclient import TestClient

from app.core.config import settings

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/users/me"


def _register(client: TestClient, email: str = "antonio@example.com") -> dict:
    response = client.post(
        REGISTER_URL,
        json={"email": email, "password": "correct horse battery staple", "name": "Antonio"},
    )
    assert response.status_code == 201
    return response.json()


def test_register_returns_access_token_and_sets_refresh_cookie(client: TestClient) -> None:
    body = _register(client)

    assert body["user"]["email"] == "antonio@example.com"
    assert body["user"]["currency"] == "EUR"
    assert "password" not in body["user"]
    assert body["access_token"]
    assert client.cookies.get("refresh_token") is not None


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    _register(client)

    response = client.post(
        REGISTER_URL,
        json={"email": "antonio@example.com", "password": "another password", "name": "Outro"},
    )

    assert response.status_code == 409


def test_login_with_correct_credentials_succeeds(client: TestClient) -> None:
    _register(client)

    response = client.post(
        LOGIN_URL, json={"email": "antonio@example.com", "password": "correct horse battery staple"}
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "antonio@example.com"


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    _register(client)

    response = client.post(LOGIN_URL, json={"email": "antonio@example.com", "password": "wrong"})

    assert response.status_code == 401


def test_me_requires_bearer_token(client: TestClient) -> None:
    assert client.get(ME_URL).status_code == 401

    body = _register(client)
    response = client.get(ME_URL, headers={"Authorization": f"Bearer {body['access_token']}"})

    assert response.status_code == 200
    assert response.json()["email"] == "antonio@example.com"


def test_update_me_requires_bearer_token(client: TestClient) -> None:
    response = client.patch(ME_URL, json={"name": "Novo Nome", "currency": "USD"})

    assert response.status_code == 401


def test_update_me_updates_name_currency_and_income(client: TestClient) -> None:
    body = _register(client)
    headers = {"Authorization": f"Bearer {body['access_token']}"}

    response = client.patch(
        ME_URL,
        json={"name": "Novo Nome", "currency": "USD", "monthly_income": "1500.50"},
        headers=headers,
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Novo Nome"
    assert updated["currency"] == "USD"
    assert updated["monthly_income"] == "1500.50"
    # A mudança persiste — não é só o valor devolvido na resposta.
    assert client.get(ME_URL, headers=headers).json() == updated


def test_update_me_can_clear_monthly_income(client: TestClient) -> None:
    body = _register(client)
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    client.patch(
        ME_URL,
        json={"name": "Antonio", "currency": "EUR", "monthly_income": "1000"},
        headers=headers,
    )

    response = client.patch(
        ME_URL,
        json={"name": "Antonio", "currency": "EUR", "monthly_income": None},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["monthly_income"] is None


def test_update_me_rejects_invalid_currency(client: TestClient) -> None:
    body = _register(client)
    headers = {"Authorization": f"Bearer {body['access_token']}"}

    response = client.patch(
        ME_URL, json={"name": "Antonio", "currency": "euros"}, headers=headers
    )

    assert response.status_code == 422


def test_update_me_rejects_negative_monthly_income(client: TestClient) -> None:
    body = _register(client)
    headers = {"Authorization": f"Bearer {body['access_token']}"}

    response = client.patch(
        ME_URL,
        json={"name": "Antonio", "currency": "EUR", "monthly_income": "-1"},
        headers=headers,
    )

    assert response.status_code == 422


def test_refresh_rotates_the_refresh_token(client: TestClient) -> None:
    _register(client)
    old_refresh_token = client.cookies.get("refresh_token")

    response = client.post(REFRESH_URL)

    assert response.status_code == 200
    new_access_token = response.json()["access_token"]
    new_refresh_token = client.cookies.get("refresh_token")
    assert new_refresh_token != old_refresh_token
    assert new_access_token

    # O refresh token antigo já não serve para obter um novo (rotação real). Reapresentado
    # de imediato conta como corrida benigna → 409 (ver teste dedicado abaixo).
    client.cookies.set("refresh_token", old_refresh_token)
    reuse_response = client.post(REFRESH_URL)
    assert reuse_response.status_code == 409


def test_immediate_refresh_token_reuse_is_treated_as_a_benign_race(client: TestClient) -> None:
    """Mesmo cookie enviado duas vezes quase em simultâneo (PWA + aba do browser, F5
    durante um pedido lento, retry de rede): o pedido atrasado falha com 409, mas a
    família de tokens fica intacta e a sessão legítima continua a funcionar."""
    _register(client)
    first_token = client.cookies.get("refresh_token")

    assert client.post(REFRESH_URL).status_code == 200
    current_token = client.cookies.get("refresh_token")

    # Reapresentar o token acabado de rodar, dentro da janela de tolerância.
    client.cookies.set("refresh_token", first_token)
    assert client.post(REFRESH_URL).status_code == 409

    # Nada foi revogado em cadeia — o token legítimo mais recente continua válido.
    client.cookies.set("refresh_token", current_token)
    assert client.post(REFRESH_URL).status_code == 200


def test_reusing_a_rotated_refresh_token_outside_the_grace_window_revokes_the_whole_family(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deteção de roubo: um token JÁ rodado, reapresentado fora da janela de tolerância,
    revoga toda a família — nem o token mais recente serve. Com a janela a 0, qualquer
    reutilização cai neste caminho (equivale a reutilizar bem depois da rotação)."""
    monkeypatch.setattr(settings, "refresh_reuse_grace_seconds", 0)

    _register(client)
    stolen_token = client.cookies.get("refresh_token")

    # Rotação normal — o utilizador legítimo obtém um token novo.
    assert client.post(REFRESH_URL).status_code == 200
    current_token = client.cookies.get("refresh_token")
    assert current_token != stolen_token

    # O atacante replica o token antigo.
    client.cookies.set("refresh_token", stolen_token)
    assert client.post(REFRESH_URL).status_code == 401

    # Consequência: o token legítimo mais recente também deixou de funcionar.
    client.cookies.set("refresh_token", current_token)
    assert client.post(REFRESH_URL).status_code == 401


def test_logout_revokes_the_refresh_token(client: TestClient) -> None:
    _register(client)

    logout_response = client.post(LOGOUT_URL)
    assert logout_response.status_code == 204

    refresh_response = client.post(REFRESH_URL)
    assert refresh_response.status_code == 401
