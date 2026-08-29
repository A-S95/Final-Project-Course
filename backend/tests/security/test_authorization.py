"""Autorização a nível de dados (IDOR): todos os recursos de domínio são sempre
filtrados por `user_id`. Um utilizador nunca acede aos objetos de outro, mesmo
sabendo o id exato — e a resposta é `404` (não `403`), de propósito, para não
confirmar sequer que o id existe.
"""

from fastapi.testclient import TestClient

from tests.api.helpers import auth_headers, create_account, create_category, register

ACCOUNTS_URL = "/api/v1/accounts"
CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"
BUDGETS_URL = "/api/v1/budgets"
GOALS_URL = "/api/v1/goals"
RECURRING_URL = "/api/v1/recurring-expenses"
HOUSEHOLDS_URL = "/api/v1/households"


def _users(client: TestClient):
    a = register(client, email="owner@example.com", name="Owner")
    b = register(client, email="attacker@example.com", name="Attacker")
    return auth_headers(a["access_token"]), auth_headers(b["access_token"])


def test_cannot_read_or_modify_another_users_account(client: TestClient) -> None:
    a, b = _users(client)
    account = create_account(client, a)

    assert account["id"] not in {x["id"] for x in client.get(ACCOUNTS_URL, headers=b).json()}
    assert client.patch(
        f"{ACCOUNTS_URL}/{account['id']}", json={"name": "hijacked"}, headers=b
    ).status_code == 404
    assert client.delete(f"{ACCOUNTS_URL}/{account['id']}", headers=b).status_code == 404


def test_cannot_read_or_modify_another_users_category(client: TestClient) -> None:
    a, b = _users(client)
    category = create_category(client, a)

    assert category["id"] not in {x["id"] for x in client.get(CATEGORIES_URL, headers=b).json()}
    assert client.patch(
        f"{CATEGORIES_URL}/{category['id']}", json={"name": "hijacked"}, headers=b
    ).status_code == 404
    assert client.delete(f"{CATEGORIES_URL}/{category['id']}", headers=b).status_code == 404


def test_cannot_touch_another_users_transaction(client: TestClient) -> None:
    a, b = _users(client)
    account = create_account(client, a, initial_balance="1000.00")
    category = create_category(client, a, type="EXPENSE")
    tx = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "10.00", "date": "2026-08-01"},
        headers=a,
    ).json()

    assert tx["id"] not in {x["id"] for x in client.get(TRANSACTIONS_URL, headers=b).json()}
    assert client.patch(
        f"{TRANSACTIONS_URL}/{tx['id']}",
        json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "999.00", "date": "2026-08-01"},
        headers=b,
    ).status_code == 404
    assert client.delete(f"{TRANSACTIONS_URL}/{tx['id']}", headers=b).status_code == 404


def test_cannot_create_transaction_referencing_another_users_account_or_category(
    client: TestClient,
) -> None:
    a, b = _users(client)
    a_account = create_account(client, a, initial_balance="500.00")
    a_category = create_category(client, a, type="EXPENSE")
    b_account = create_account(client, b, initial_balance="500.00")
    b_category = create_category(client, b, type="EXPENSE")

    # B usa a conta de A:
    assert client.post(
        TRANSACTIONS_URL,
        json={"account_id": a_account["id"], "category_id": b_category["id"], "type": "EXPENSE",
              "amount": "10.00", "date": "2026-08-01"},
        headers=b,
    ).status_code == 404
    # B usa a categoria de A:
    assert client.post(
        TRANSACTIONS_URL,
        json={"account_id": b_account["id"], "category_id": a_category["id"], "type": "EXPENSE",
              "amount": "10.00", "date": "2026-08-01"},
        headers=b,
    ).status_code == 404
    # B faz uma transferência para a conta de A:
    assert client.post(
        TRANSACTIONS_URL,
        json={"account_id": b_account["id"], "destination_account_id": a_account["id"],
              "type": "TRANSFER", "amount": "10.00", "date": "2026-08-01"},
        headers=b,
    ).status_code == 404
    # A conta de A não se mexeu.
    a_accounts = client.get(ACCOUNTS_URL, headers=a).json()
    a_view = next(x for x in a_accounts if x["id"] == a_account["id"])
    assert a_view["current_balance"] == "500.00"


def test_cannot_touch_another_users_budget(client: TestClient) -> None:
    a, b = _users(client)
    category = create_category(client, a, type="EXPENSE")
    budget = client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=a,
    ).json()

    assert client.patch(
        f"{BUDGETS_URL}/{budget['id']}", json={"amount": "1.00"}, headers=b
    ).status_code == 404
    assert client.delete(f"{BUDGETS_URL}/{budget['id']}", headers=b).status_code == 404
    assert client.get(BUDGETS_URL, params={"month": "2026-08-01"}, headers=b).json() == []


def test_cannot_touch_another_users_goal(client: TestClient) -> None:
    a, b = _users(client)
    goal = client.post(
        GOALS_URL, json={"name": "A goal", "target_amount": "1000.00"}, headers=a
    ).json()

    assert client.patch(
        f"{GOALS_URL}/{goal['id']}", json={"name": "x"}, headers=b
    ).status_code == 404
    assert client.post(
        f"{GOALS_URL}/{goal['id']}/contributions", json={"amount": "50.00"}, headers=b
    ).status_code == 404
    assert client.delete(f"{GOALS_URL}/{goal['id']}", headers=b).status_code == 404


def test_cannot_touch_another_users_recurring_expense(client: TestClient) -> None:
    a, b = _users(client)
    account = create_account(client, a)
    category = create_category(client, a, type="EXPENSE")
    recurring = client.post(
        RECURRING_URL,
        json={"account_id": account["id"], "category_id": category["id"], "description": "Renda",
              "amount": "100.00", "frequency": "MONTHLY", "next_occurrence": "2026-08-01",
              "active": True},
        headers=a,
    ).json()

    assert client.patch(
        f"{RECURRING_URL}/{recurring['id']}", json={"amount": "1.00"}, headers=b
    ).status_code == 404
    assert client.delete(f"{RECURRING_URL}/{recurring['id']}", headers=b).status_code == 404
    assert client.get(RECURRING_URL, headers=b).json() == []


def test_cannot_cancel_or_accept_someone_elses_household_invite(client: TestClient) -> None:
    a = register(client, email="a@example.com")
    b = register(client, email="b@example.com")
    c = register(client, email="c@example.com")
    ha, hb, hc = (auth_headers(u["access_token"]) for u in (a, b, c))

    client.post(HOUSEHOLDS_URL, json={"name": "Casa A"}, headers=ha)
    invite_id = client.post(
        f"{HOUSEHOLDS_URL}/me/invites", json={"email": "b@example.com"}, headers=ha
    ).json()["id"]

    # C (terceiro) não pode aceitar um convite dirigido a B:
    assert client.post(
        f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=hc
    ).status_code == 404
    # C não pertence a nenhum agregado -> não pode cancelar o convite de A:
    assert client.delete(
        f"{HOUSEHOLDS_URL}/me/invites/{invite_id}", headers=hc
    ).status_code == 404
    # O convite continua válido para B.
    b_invites = client.get(f"{HOUSEHOLDS_URL}/invites", headers=hb).json()
    assert invite_id in {i["id"] for i in b_invites}


def test_unauthorized_access_returns_404_not_403(client: TestClient) -> None:
    """A escolha deliberada: nunca revelar que o id existe (secção 8 do ARCHITECTURE.md)."""
    a, b = _users(client)
    account = create_account(client, a)
    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}", json={"name": "x"}, headers=b
    )
    assert response.status_code == 404
    assert response.status_code != 403
