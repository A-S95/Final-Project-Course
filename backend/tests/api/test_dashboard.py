from datetime import date

from fastapi.testclient import TestClient

from tests.api.helpers import create_account, create_category, register_and_get_headers

TRANSACTIONS_URL = "/api/v1/transactions"
DASHBOARD_URL = "/api/v1/dashboard"


def _add_transaction(client: TestClient, headers: dict, **overrides: object) -> dict:
    payload = {"type": "EXPENSE", "amount": "10.00", "date": "2026-08-10", **overrides}
    response = client.post(TRANSACTIONS_URL, json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_dashboard_is_empty_for_new_user(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    response = client.get(DASHBOARD_URL, params={"month": "2026-08-01"}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["month"] == "2026-08-01"
    assert body["total_balance"] == "0.00"
    assert body["total_income"] == "0.00"
    assert body["total_expenses"] == "0.00"
    assert body["net"] == "0.00"
    assert body["savings_rate"] is None
    assert body["expenses_by_category"] == []


def test_dashboard_totals_and_savings_rate(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    salary = create_category(client, headers, name="Salário", type="INCOME")
    food = create_category(client, headers, name="Alimentação", type="EXPENSE")

    _add_transaction(
        client, headers, account_id=account["id"], category_id=salary["id"],
        type="INCOME", amount="1000.00", date="2026-08-01",
    )
    _add_transaction(
        client, headers, account_id=account["id"], category_id=food["id"],
        type="EXPENSE", amount="250.00", date="2026-08-15",
    )

    body = client.get(
        DASHBOARD_URL, params={"month": "2026-08-20"}, headers=headers
    ).json()

    assert body["total_income"] == "1000.00"
    assert body["total_expenses"] == "250.00"
    assert body["net"] == "750.00"
    assert body["savings_rate"] == 75.0
    assert body["total_balance"] == "750.00"


def test_dashboard_ignores_transfers_in_income_and_expenses(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    origin = create_account(client, headers, name="Millennium", initial_balance="500.00")
    destination = create_account(client, headers, name="Revolut", initial_balance="0.00")

    _add_transaction(
        client, headers, account_id=origin["id"], destination_account_id=destination["id"],
        type="TRANSFER", amount="200.00", date="2026-08-05",
    )

    body = client.get(DASHBOARD_URL, params={"month": "2026-08-01"}, headers=headers).json()

    assert body["total_income"] == "0.00"
    assert body["total_expenses"] == "0.00"
    # A transferência mexe nos saldos, por isso o saldo global mantém-se.
    assert body["total_balance"] == "500.00"


def test_dashboard_only_counts_the_selected_month(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    food = create_category(client, headers, name="Alimentação", type="EXPENSE")

    _add_transaction(
        client, headers, account_id=account["id"], category_id=food["id"],
        type="EXPENSE", amount="30.00", date="2026-07-31",
    )
    _add_transaction(
        client, headers, account_id=account["id"], category_id=food["id"],
        type="EXPENSE", amount="40.00", date="2026-08-01",
    )

    body = client.get(DASHBOARD_URL, params={"month": "2026-08-15"}, headers=headers).json()

    assert body["total_expenses"] == "40.00"


def test_dashboard_expenses_by_category_are_grouped_and_sorted(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    food = create_category(client, headers, name="Alimentação", type="EXPENSE")
    transport = create_category(client, headers, name="Transporte", type="EXPENSE")

    _add_transaction(
        client, headers, account_id=account["id"], category_id=food["id"],
        type="EXPENSE", amount="20.00", date="2026-08-02",
    )
    _add_transaction(
        client, headers, account_id=account["id"], category_id=food["id"],
        type="EXPENSE", amount="15.00", date="2026-08-09",
    )
    _add_transaction(
        client, headers, account_id=account["id"], category_id=transport["id"],
        type="EXPENSE", amount="50.00", date="2026-08-09",
    )

    breakdown = client.get(
        DASHBOARD_URL, params={"month": "2026-08-01"}, headers=headers
    ).json()["expenses_by_category"]

    assert [(item["name"], item["total"]) for item in breakdown] == [
        ("Transporte", "50.00"),
        ("Alimentação", "35.00"),
    ]


def test_dashboard_defaults_to_current_month(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    food = create_category(client, headers, name="Alimentação", type="EXPENSE")
    _add_transaction(
        client, headers, account_id=account["id"], category_id=food["id"],
        type="EXPENSE", amount="12.00", date=date.today().isoformat(),
    )

    body = client.get(DASHBOARD_URL, headers=headers).json()

    assert body["month"] == date.today().replace(day=1).isoformat()
    assert body["total_expenses"] == "12.00"


def test_dashboard_is_isolated_per_user(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    account_a = create_account(client, headers_a, initial_balance="0.00")
    food_a = create_category(client, headers_a, name="Alimentação", type="EXPENSE")
    _add_transaction(
        client, headers_a, account_id=account_a["id"], category_id=food_a["id"],
        type="EXPENSE", amount="99.00", date="2026-08-03",
    )

    body_b = client.get(DASHBOARD_URL, params={"month": "2026-08-01"}, headers=headers_b).json()

    assert body_b["total_expenses"] == "0.00"
    assert body_b["total_balance"] == "0.00"


def test_dashboard_requires_authentication(client: TestClient) -> None:
    assert client.get(DASHBOARD_URL).status_code == 401
