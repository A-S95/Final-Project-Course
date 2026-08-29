from datetime import date, timedelta

from fastapi.testclient import TestClient

from tests.api.helpers import create_account, create_category, register_and_get_headers

RECURRING_URL = "/api/v1/recurring-expenses"
ACCOUNTS_URL = "/api/v1/accounts"
CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"


def _account_balance(client: TestClient, headers: dict, account_id: str) -> str:
    accounts = client.get(ACCOUNTS_URL, headers=headers).json()
    return next(a["current_balance"] for a in accounts if a["id"] == account_id)


def _create(client: TestClient, headers: dict, account_id: str, category_id: str, **overrides):
    payload = {
        "account_id": account_id,
        "category_id": category_id,
        "description": "Renda",
        "amount": "500.00",
        "frequency": "MONTHLY",
        "next_occurrence": date.today().isoformat(),
        **overrides,
    }
    return client.post(RECURRING_URL, json=payload, headers=headers)


def test_create_recurring_expense(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")

    response = _create(
        client, headers, account["id"], category["id"], next_occurrence="2026-09-15"
    )

    assert response.status_code == 201
    body = response.json()
    assert body["description"] == "Renda"
    assert body["day_of_month"] == 15  # derivado de next_occurrence
    assert body["account_name"] == account["name"]
    assert body["category_name"] == category["name"]
    assert body["active"] is True


def test_recurring_expense_needs_an_expense_category(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    income = create_category(client, headers, name="Salário", type="INCOME")

    assert _create(client, headers, account["id"], income["id"]).status_code == 422


def test_recurring_expense_with_unknown_account_is_404(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, type="EXPENSE")

    response = _create(
        client, headers, "00000000-0000-0000-0000-000000000000", category["id"]
    )
    assert response.status_code == 404


def test_generate_creates_a_transaction_and_advances(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, name="Casa", type="EXPENSE")
    recurring = _create(
        client, headers, account["id"], category["id"],
        amount="300.00", next_occurrence=date.today().isoformat(),
    ).json()

    result = client.post(f"{RECURRING_URL}/generate", headers=headers)
    assert result.status_code == 200
    assert result.json()["generated"] == 1

    transactions = client.get(TRANSACTIONS_URL, headers=headers).json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Renda"
    assert transactions[0]["amount"] == "300.00"
    assert _account_balance(client, headers, account["id"]) == "700.00"

    updated = next(
        r for r in client.get(RECURRING_URL, headers=headers).json() if r["id"] == recurring["id"]
    )
    assert updated["next_occurrence"] > date.today().isoformat()
    assert updated["is_due"] is False

    # Idempotente: correr outra vez não gera nada.
    assert client.post(f"{RECURRING_URL}/generate", headers=headers).json()["generated"] == 0


def test_generate_catches_up_on_missed_months(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="10000.00")
    category = create_category(client, headers, type="EXPENSE")
    start = date.today().replace(day=1)
    # Recua ~5 meses mantendo dia 1.
    for _ in range(5):
        start = (start - timedelta(days=1)).replace(day=1)
    _create(
        client, headers, account["id"], category["id"],
        amount="100.00", next_occurrence=start.isoformat(),
    )

    generated = client.post(f"{RECURRING_URL}/generate", headers=headers).json()["generated"]

    assert generated >= 5
    transactions = client.get(TRANSACTIONS_URL, headers=headers).json()
    assert len(transactions) == generated
    expected_balance = 10000 - generated * 100
    assert _account_balance(client, headers, account["id"]) == f"{expected_balance}.00"


def test_generate_skips_inactive_and_future(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, type="EXPENSE")
    # Inativa, vencida.
    _create(
        client, headers, account["id"], category["id"],
        next_occurrence=date.today().isoformat(), active=False,
    )
    # Ativa, mas no futuro.
    future = (date.today() + timedelta(days=40)).isoformat()
    _create(client, headers, account["id"], category["id"], next_occurrence=future)

    assert client.post(f"{RECURRING_URL}/generate", headers=headers).json()["generated"] == 0
    assert client.get(TRANSACTIONS_URL, headers=headers).json() == []


def test_update_recurring_expense(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    recurring = _create(client, headers, account["id"], category["id"]).json()

    response = client.patch(
        f"{RECURRING_URL}/{recurring['id']}",
        json={"amount": "750.00", "active": False, "next_occurrence": "2027-01-05"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == "750.00"
    assert body["active"] is False
    assert body["day_of_month"] == 5
    assert body["next_occurrence"] == "2027-01-05"


def test_delete_recurring_expense(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    recurring = _create(client, headers, account["id"], category["id"]).json()

    assert client.delete(f"{RECURRING_URL}/{recurring['id']}", headers=headers).status_code == 204
    assert client.get(RECURRING_URL, headers=headers).json() == []


def test_recurring_expenses_are_isolated_per_user(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    account = create_account(client, headers_a)
    category = create_category(client, headers_a, type="EXPENSE")
    recurring = _create(client, headers_a, account["id"], category["id"]).json()

    assert client.get(RECURRING_URL, headers=headers_b).json() == []
    assert client.delete(
        f"{RECURRING_URL}/{recurring['id']}", headers=headers_b
    ).status_code == 404


def test_deleting_account_with_a_recurring_expense_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    _create(client, headers, account["id"], category["id"])

    assert client.delete(f"{ACCOUNTS_URL}/{account['id']}", headers=headers).status_code == 409


def test_deleting_category_with_a_recurring_expense_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    _create(client, headers, account["id"], category["id"])

    assert client.delete(f"{CATEGORIES_URL}/{category['id']}", headers=headers).status_code == 409


def test_recurring_expenses_require_authentication(client: TestClient) -> None:
    assert client.get(RECURRING_URL).status_code == 401
    assert client.post(f"{RECURRING_URL}/generate").status_code == 401
