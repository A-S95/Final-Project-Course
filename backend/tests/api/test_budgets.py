from fastapi.testclient import TestClient

from tests.api.helpers import create_account, create_category, register_and_get_headers

BUDGETS_URL = "/api/v1/budgets"
CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"


def _spend(client: TestClient, headers: dict, account_id: str, category_id: str, amount: str,
           date: str) -> None:
    response = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account_id, "category_id": category_id, "type": "EXPENSE",
              "amount": amount, "date": date},
        headers=headers,
    )
    assert response.status_code == 201, response.text


def test_create_budget_starts_with_zero_spent(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, name="Alimentação", type="EXPENSE")

    response = client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-14", "amount": "300.00"},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["category_name"] == "Alimentação"
    # Qualquer dia do mês é normalizado para o dia 1.
    assert body["period_month"] == "2026-08-01"
    assert body["amount"] == "300.00"
    assert body["spent"] == "0.00"
    assert body["remaining"] == "300.00"
    assert body["percentage"] == 0.0


def test_budget_for_income_category_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, name="Salário", type="INCOME")

    response = client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    )

    assert response.status_code == 422


def test_budget_for_unknown_category_is_404(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    response = client.post(
        BUDGETS_URL,
        json={
            "category_id": "00000000-0000-0000-0000-000000000000",
            "period_month": "2026-08-01",
            "amount": "100.00",
        },
        headers=headers,
    )

    assert response.status_code == 404


def test_duplicate_budget_same_category_and_month_is_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, type="EXPENSE")
    payload = {"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"}

    assert client.post(BUDGETS_URL, json=payload, headers=headers).status_code == 201
    assert client.post(BUDGETS_URL, json=payload, headers=headers).status_code == 409
    # Mas o mês seguinte já pode ter o seu próprio orçamento.
    payload_sep = {**payload, "period_month": "2026-09-01"}
    assert client.post(BUDGETS_URL, json=payload_sep, headers=headers).status_code == 201


def test_budget_spent_reflects_month_transactions(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, name="Alimentação", type="EXPENSE")
    budget = client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "200.00"},
        headers=headers,
    ).json()

    _spend(client, headers, account["id"], category["id"], "50.00", "2026-08-03")
    _spend(client, headers, account["id"], category["id"], "30.00", "2026-08-20")
    # Fora do mês — não conta.
    _spend(client, headers, account["id"], category["id"], "999.00", "2026-07-31")

    listed = client.get(BUDGETS_URL, params={"month": "2026-08-10"}, headers=headers).json()
    assert len(listed) == 1
    assert listed[0]["id"] == budget["id"]
    assert listed[0]["spent"] == "80.00"
    assert listed[0]["remaining"] == "120.00"
    assert listed[0]["percentage"] == 40.0


def test_budget_can_go_over(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    )
    _spend(client, headers, account["id"], category["id"], "150.00", "2026-08-05")

    listed = client.get(BUDGETS_URL, params={"month": "2026-08-01"}, headers=headers).json()
    assert listed[0]["spent"] == "150.00"
    assert listed[0]["remaining"] == "-50.00"
    assert listed[0]["percentage"] == 150.0


def test_list_budgets_is_scoped_to_the_month(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    )
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-09-01", "amount": "120.00"},
        headers=headers,
    )

    august = client.get(BUDGETS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    assert [b["amount"] for b in august] == ["100.00"]


def test_update_budget_amount_recomputes_progress(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, type="EXPENSE")
    budget = client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    ).json()
    _spend(client, headers, account["id"], category["id"], "60.00", "2026-08-05")

    response = client.patch(
        f"{BUDGETS_URL}/{budget['id']}", json={"amount": "200.00"}, headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == "200.00"
    assert body["spent"] == "60.00"
    assert body["remaining"] == "140.00"
    assert body["percentage"] == 30.0


def test_delete_budget(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, type="EXPENSE")
    budget = client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    ).json()

    assert client.delete(f"{BUDGETS_URL}/{budget['id']}", headers=headers).status_code == 204
    assert client.get(BUDGETS_URL, params={"month": "2026-08-01"}, headers=headers).json() == []


def test_budgets_are_isolated_per_user(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    category_a = create_category(client, headers_a, type="EXPENSE")
    budget_a = client.post(
        BUDGETS_URL,
        json={"category_id": category_a["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers_a,
    ).json()

    assert client.get(BUDGETS_URL, params={"month": "2026-08-01"}, headers=headers_b).json() == []
    assert client.patch(
        f"{BUDGETS_URL}/{budget_a['id']}", json={"amount": "5.00"}, headers=headers_b
    ).status_code == 404


def test_deleting_category_with_a_budget_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    )

    response = client.delete(f"{CATEGORIES_URL}/{category['id']}", headers=headers)
    assert response.status_code == 409


def test_budgets_require_authentication(client: TestClient) -> None:
    assert client.get(BUDGETS_URL).status_code == 401
