from fastapi.testclient import TestClient

REGISTER_URL = "/api/v1/auth/register"
ACCOUNTS_URL = "/api/v1/accounts"
CATEGORIES_URL = "/api/v1/categories"


def register(
    client: TestClient, email: str = "antonio@example.com", name: str = "Antonio"
) -> dict:
    """Regista um utilizador e devolve o corpo completo (`access_token` + `user`)."""
    response = client.post(
        REGISTER_URL,
        json={"email": email, "password": "correct horse battery staple", "name": name},
    )
    assert response.status_code == 201
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_and_get_headers(client: TestClient, email: str = "antonio@example.com") -> dict:
    return auth_headers(register(client, email)["access_token"])


def create_account(
    client: TestClient,
    headers: dict,
    *,
    name: str = "Millennium",
    type: str = "BANK",
    initial_balance: str = "100.00",
) -> dict:
    response = client.post(
        ACCOUNTS_URL,
        json={"name": name, "type": type, "initial_balance": initial_balance},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_category(
    client: TestClient, headers: dict, *, name: str = "Alimentação", type: str = "EXPENSE"
) -> dict:
    response = client.post(CATEGORIES_URL, json={"name": name, "type": type}, headers=headers)
    assert response.status_code == 201
    return response.json()
