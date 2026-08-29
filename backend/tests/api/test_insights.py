import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services import insights_service
from tests.api.helpers import (
    auth_headers,
    create_account,
    create_category,
    register,
    register_and_get_headers,
)

INSIGHTS_URL = "/api/v1/insights"
TRANSACTIONS_URL = "/api/v1/transactions"
BUDGETS_URL = "/api/v1/budgets"
GOALS_URL = "/api/v1/goals"


def _tx(client, headers, account, category, type_, amount, date_):
    r = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account, "category_id": category, "type": type_,
              "amount": amount, "date": date_},
        headers=headers,
    )
    assert r.status_code == 201, r.text


def _rules(items) -> set[str]:
    return {i["rule"] for i in items}


def test_no_data_no_insights(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    assert client.get(INSIGHTS_URL, params={"month": "2026-08-01"}, headers=headers).json() == []


def test_budget_exceeded_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, name="Casa", type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    )
    _tx(client, headers, account["id"], category["id"], "EXPENSE", "150.00", "2026-08-10")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    exceeded = next(i for i in items if i["rule"] == "budget_exceeded")
    assert exceeded["severity"] == "warning"
    assert "Casa" in exceeded["title"]
    assert "150,00" in exceeded["detail"] and "150%" in exceeded["detail"]


def test_budget_near_limit_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "100.00"},
        headers=headers,
    )
    _tx(client, headers, account["id"], category["id"], "EXPENSE", "85.00", "2026-08-05")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-20"}, headers=headers).json()
    assert "budget_near_limit" in _rules(items)
    assert "budget_exceeded" not in _rules(items)


def test_budget_pace_insight(client: TestClient, db_session: Session) -> None:
    body = register(client)
    headers = auth_headers(body["access_token"])
    user_id = body["user"]["id"]
    account = create_account(client, headers, initial_balance="2000.00")
    category = create_category(client, headers, name="Lazer", type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "1000.00"},
        headers=headers,
    )
    _tx(client, headers, account["id"], category["id"], "EXPENSE", "400.00", "2026-08-01")

    # Dia 3 de agosto: ~10% do mês decorrido, mas 40% do orçamento gasto.
    items = insights_service.get_insights(
        db_session,
        user_id=uuid.UUID(user_id),
        month=date(2026, 8, 1),
        today=date(2026, 8, 3),
    )
    rules = {i.rule for i in items}
    assert "budget_pace" in rules
    assert "budget_exceeded" not in rules


def test_expenses_up_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    inc = create_category(client, headers, name="Salário", type="INCOME")
    exp = create_category(client, headers, name="Casa", type="EXPENSE")
    _tx(client, headers, account["id"], inc["id"], "INCOME", "3000.00", "2026-08-01")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "500.00", "2026-07-10")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "900.00", "2026-08-10")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    up = next(i for i in items if i["rule"] == "expenses_up")
    assert up["severity"] == "warning"
    assert "80%" in up["title"]  # 900 vs 500 -> +80%


def test_expenses_down_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    exp = create_category(client, headers, type="EXPENSE")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "1000.00", "2026-07-10")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "600.00", "2026-08-10")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    down = next(i for i in items if i["rule"] == "expenses_down")
    assert down["severity"] == "positive"


def test_negative_net_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    inc = create_category(client, headers, name="Salário", type="INCOME")
    exp = create_category(client, headers, name="Casa", type="EXPENSE")
    _tx(client, headers, account["id"], inc["id"], "INCOME", "500.00", "2026-08-02")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "800.00", "2026-08-10")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    assert "negative_net" in _rules(items)


def test_healthy_savings_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    inc = create_category(client, headers, name="Salário", type="INCOME")
    exp = create_category(client, headers, name="Casa", type="EXPENSE")
    _tx(client, headers, account["id"], inc["id"], "INCOME", "2000.00", "2026-08-02")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "1000.00", "2026-08-10")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    healthy = next(i for i in items if i["rule"] == "healthy_savings")
    assert healthy["severity"] == "positive"
    assert "50" in healthy["detail"]


def test_goal_off_pace_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    deadline = (date.today() + timedelta(days=60)).isoformat()
    client.post(
        GOALS_URL,
        json={"name": "Carro", "target_amount": "6000.00", "current_amount": "0.00",
              "deadline": deadline},
        headers=headers,
    )

    # Sem receitas/despesas -> poupança 0 < contribuição mensal necessária.
    items = client.get(INSIGHTS_URL, headers=headers).json()
    off_pace = next(i for i in items if i["rule"] == "goal_off_pace")
    assert off_pace["severity"] == "warning"
    assert "Carro" in off_pace["title"]


def test_goal_deadline_passed_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    past = (date.today() - timedelta(days=5)).isoformat()
    client.post(
        GOALS_URL,
        json={"name": "Viagem", "target_amount": "500.00", "current_amount": "100.00",
              "deadline": past},
        headers=headers,
    )

    items = client.get(INSIGHTS_URL, headers=headers).json()
    assert "goal_deadline_passed" in _rules(items)


def test_warnings_are_listed_before_positives(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    inc = create_category(client, headers, name="Salário", type="INCOME")
    exp = create_category(client, headers, name="Casa", type="EXPENSE")
    # Poupança saudável (positivo) + despesas muito abaixo do mês anterior (positivo)
    # + orçamento ultrapassado (aviso).
    _tx(client, headers, account["id"], inc["id"], "INCOME", "2000.00", "2026-08-02")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "1000.00", "2026-07-10")
    _tx(client, headers, account["id"], exp["id"], "EXPENSE", "300.00", "2026-08-10")
    other = create_category(client, headers, name="Lazer", type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": other["id"], "period_month": "2026-08-01", "amount": "50.00"},
        headers=headers,
    )
    _tx(client, headers, account["id"], other["id"], "EXPENSE", "120.00", "2026-08-11")

    items = client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers).json()
    severities = [i["severity"] for i in items]
    assert "warning" in severities and "positive" in severities
    assert severities.index("warning") < severities.index("positive")


def test_insights_isolated_per_user(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    account = create_account(client, headers_a, initial_balance="1000.00")
    category = create_category(client, headers_a, type="EXPENSE")
    client.post(
        BUDGETS_URL,
        json={"category_id": category["id"], "period_month": "2026-08-01", "amount": "10.00"},
        headers=headers_a,
    )
    _tx(client, headers_a, account["id"], category["id"], "EXPENSE", "50.00", "2026-08-10")

    assert client.get(INSIGHTS_URL, params={"month": "2026-08-15"}, headers=headers_b).json() == []


def test_card_expiring_soon_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    soon = (date.today() + timedelta(days=10)).isoformat()
    create_account(client, headers, name="Universo", type="CREDIT_CARD",
                    card_expiration_date=soon)

    items = client.get(INSIGHTS_URL, headers=headers).json()
    insight = next(i for i in items if i["rule"] == "card_expiring_soon")
    assert insight["severity"] == "warning"
    assert "Universo" in insight["title"]


def test_card_expired_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    past = (date.today() - timedelta(days=3)).isoformat()
    create_account(client, headers, name="Revolut", type="CREDIT_CARD",
                    card_expiration_date=past)

    items = client.get(INSIGHTS_URL, headers=headers).json()
    assert "card_expired" in _rules(items)


def test_card_expiration_far_away_no_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    far = (date.today() + timedelta(days=200)).isoformat()
    create_account(client, headers, name="Revolut", type="CREDIT_CARD",
                    card_expiration_date=far)

    items = client.get(INSIGHTS_URL, headers=headers).json()
    assert "card_expiring_soon" not in _rules(items)
    assert "card_expired" not in _rules(items)


def test_card_below_plafond_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    create_account(client, headers, name="Universo", type="CREDIT_CARD",
                    initial_balance="400.00", card_plafond="1000.00")

    items = client.get(INSIGHTS_URL, headers=headers).json()
    insight = next(i for i in items if i["rule"] == "card_below_plafond")
    assert insight["severity"] == "warning"
    assert "Universo" in insight["title"]
    assert "600,00" in insight["detail"]  # falta recarregar 1000 - 400


def test_card_at_plafond_no_insight(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    create_account(client, headers, name="Universo", type="CREDIT_CARD",
                    initial_balance="1000.00", card_plafond="1000.00")

    items = client.get(INSIGHTS_URL, headers=headers).json()
    assert "card_below_plafond" not in _rules(items)


def test_card_insights_only_on_current_month(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    past = (date.today() - timedelta(days=3)).isoformat()
    create_account(client, headers, name="Revolut", type="CREDIT_CARD",
                    card_expiration_date=past)

    items = client.get(INSIGHTS_URL, params={"month": "2020-01-01"}, headers=headers).json()
    assert "card_expired" not in _rules(items)


def test_insights_require_authentication(client: TestClient) -> None:
    assert client.get(INSIGHTS_URL).status_code == 401
