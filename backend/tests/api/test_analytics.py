from fastapi.testclient import TestClient

from tests.api.helpers import create_account, create_category, register_and_get_headers

TRANSACTIONS_URL = "/api/v1/transactions"
COMPARISON_URL = "/api/v1/analytics/monthly-comparison"
TREND_URL = "/api/v1/analytics/monthly-trend"


def _spend(client: TestClient, headers, account_id, category_id, type_, amount, date_):
    response = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account_id, "category_id": category_id, "type": type_,
              "amount": amount, "date": date_},
        headers=headers,
    )
    assert response.status_code == 201, response.text


def _setup(client: TestClient, headers):
    account = create_account(client, headers, initial_balance="0.00")
    income_cat = create_category(client, headers, name="Salário", type="INCOME")
    expense_cat = create_category(client, headers, name="Casa", type="EXPENSE")
    return account["id"], income_cat["id"], expense_cat["id"]


def test_monthly_comparison_computes_deltas(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account, inc, exp = _setup(client, headers)

    # Maio (anterior)
    _spend(client, headers, account, inc, "INCOME", "1500.00", "2026-05-03")
    _spend(client, headers, account, exp, "EXPENSE", "800.00", "2026-05-10")
    # Junho (atual)
    _spend(client, headers, account, inc, "INCOME", "2000.00", "2026-06-03")
    _spend(client, headers, account, exp, "EXPENSE", "500.00", "2026-06-12")

    body = client.get(COMPARISON_URL, params={"month": "2026-06-20"}, headers=headers).json()

    assert body["current"]["month"] == "2026-06-01"
    assert body["current"]["total_income"] == "2000.00"
    assert body["current"]["total_expenses"] == "500.00"
    assert body["current"]["net"] == "1500.00"
    assert body["previous"]["month"] == "2026-05-01"
    assert body["previous"]["net"] == "700.00"

    assert body["income_change"] == "500.00"
    assert body["expenses_change"] == "-300.00"
    assert body["net_change"] == "800.00"
    assert body["income_change_pct"] == 33.3  # 500 / 1500
    assert body["expenses_change_pct"] == -37.5  # -300 / 800


def test_monthly_comparison_with_no_previous_data(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account, inc, exp = _setup(client, headers)
    _spend(client, headers, account, inc, "INCOME", "1000.00", "2026-06-05")

    body = client.get(COMPARISON_URL, params={"month": "2026-06-01"}, headers=headers).json()

    assert body["previous"]["total_income"] == "0.00"
    assert body["income_change"] == "1000.00"
    assert body["income_change_pct"] is None  # dividir por zero
    assert body["expenses_change_pct"] is None


def test_monthly_trend_returns_ordered_points(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account, inc, exp = _setup(client, headers)
    _spend(client, headers, account, exp, "EXPENSE", "100.00", "2026-04-10")
    _spend(client, headers, account, exp, "EXPENSE", "200.00", "2026-06-10")

    body = client.get(
        TREND_URL, params={"months": 4, "month": "2026-06-15"}, headers=headers
    ).json()

    months = [p["month"] for p in body["points"]]
    assert months == ["2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01"]
    expenses = [p["total_expenses"] for p in body["points"]]
    assert expenses == ["0.00", "100.00", "0.00", "200.00"]


def test_monthly_trend_rejects_out_of_range_months(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    assert client.get(TREND_URL, params={"months": 1}, headers=headers).status_code == 422
    assert client.get(TREND_URL, params={"months": 25}, headers=headers).status_code == 422


def test_analytics_is_isolated_per_user(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    account, inc, exp = _setup(client, headers_a)
    _spend(client, headers_a, account, inc, "INCOME", "999.00", "2026-06-05")

    body = client.get(COMPARISON_URL, params={"month": "2026-06-01"}, headers=headers_b).json()
    assert body["current"]["total_income"] == "0.00"


def test_analytics_requires_authentication(client: TestClient) -> None:
    assert client.get(COMPARISON_URL).status_code == 401
    assert client.get(TREND_URL).status_code == 401
