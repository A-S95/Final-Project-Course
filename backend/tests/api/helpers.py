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
    card_expiration_date: str | None = None,
    card_plafond: str | None = None,
) -> dict:
    payload = {"name": name, "type": type, "initial_balance": initial_balance}
    if card_expiration_date is not None:
        payload["card_expiration_date"] = card_expiration_date
    if card_plafond is not None:
        payload["card_plafond"] = card_plafond
    response = client.post(ACCOUNTS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def create_category(
    client: TestClient, headers: dict, *, name: str = "Alimentação", type: str = "EXPENSE"
) -> dict:
    response = client.post(CATEGORIES_URL, json={"name": name, "type": type}, headers=headers)
    if response.status_code == 409:
        # Já existe — quase sempre uma das categorias-padrão criadas no registo.
        existing = client.get(CATEGORIES_URL, headers=headers).json()
        return next(c for c in existing if c["name"] == name)
    assert response.status_code == 201
    return response.json()


# Os PATCH de conta/categoria/objetivo levam o formulário completo (a UI reenvia
# tudo — ver schemas). Estes helpers partem do objeto atual e aplicam só as
# alterações do teste.
def account_update_body(account: dict, **changes: object) -> dict:
    body = {
        k: account[k]
        for k in ("name", "type", "initial_balance", "card_expiration_date", "card_plafond")
    }
    return {**body, **changes}


def category_update_body(category: dict, **changes: object) -> dict:
    return {**{k: category[k] for k in ("name", "type", "icon", "color")}, **changes}


def goal_update_body(goal: dict, **changes: object) -> dict:
    keys = ("name", "target_amount", "current_amount", "deadline")
    return {**{k: goal[k] for k in keys}, **changes}
