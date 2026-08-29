"""Robustez de input: valores que a base de dados não aceitaria (overflow de
NUMERIC, casas decimais a mais, strings gigantes) são rejeitados com 422 pela
validação Pydantic, antes de chegarem ao insert — nunca um 500. E campos extra
no corpo do pedido são ignorados (sem mass-assignment).
"""

from fastapi.testclient import TestClient

from tests.api.helpers import (
    auth_headers,
    create_account,
    create_category,
    register,
    register_and_get_headers,
)

ACCOUNTS_URL = "/api/v1/accounts"
CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"
GOALS_URL = "/api/v1/goals"


def test_numeric_overflow_is_rejected_with_422(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    # NUMERIC(12,2): máximo 10 dígitos inteiros. 14 dígitos -> 422, não 500.
    response = client.post(
        ACCOUNTS_URL,
        json={"name": "Big", "type": "BANK", "initial_balance": "99999999999999.99"},
        headers=headers,
    )
    assert response.status_code == 422


def test_too_many_decimal_places_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    category = create_category(client, headers, type="EXPENSE")
    response = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "10.123", "date": "2026-08-01"},
        headers=headers,
    )
    assert response.status_code == 422


def test_non_positive_amounts_are_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    category = create_category(client, headers, type="EXPENSE")
    for bad_amount in ["0", "0.00", "-5.00"]:
        response = client.post(
            TRANSACTIONS_URL,
            json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
                  "amount": bad_amount, "date": "2026-08-01"},
            headers=headers,
        )
        assert response.status_code == 422, (bad_amount, response.status_code)


def test_oversized_strings_are_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    huge = "A" * 5000
    assert client.post(
        CATEGORIES_URL, json={"name": huge, "type": "EXPENSE"}, headers=headers
    ).status_code == 422
    assert client.post(
        ACCOUNTS_URL,
        json={"name": huge, "type": "BANK", "initial_balance": "0.00"},
        headers=headers,
    ).status_code == 422
    assert client.post(
        GOALS_URL, json={"name": huge, "target_amount": "100.00"}, headers=headers
    ).status_code == 422


def test_extra_fields_in_body_are_ignored_no_mass_assignment(client: TestClient) -> None:
    a_body = register(client, email="a@example.com")
    b_body = register(client, email="b@example.com")
    a = auth_headers(a_body["access_token"])
    b = auth_headers(b_body["access_token"])

    # A tenta forçar o dono, o id e o saldo atual da conta.
    created = client.post(
        ACCOUNTS_URL,
        json={
            "name": "Trojan",
            "type": "BANK",
            "initial_balance": "100.00",
            "user_id": b_body["user"]["id"],  # tentativa de atribuir a B
            "id": "11111111-1111-1111-1111-111111111111",  # tentativa de fixar o id
            "current_balance": "999999.00",  # tentativa de inflar o saldo
        },
        headers=a,
    )
    assert created.status_code == 201
    account = created.json()
    assert account["id"] != "11111111-1111-1111-1111-111111111111"
    assert account["current_balance"] == "100.00"  # = initial_balance, não 999999

    # A conta é de A, não de B.
    assert account["id"] in {x["id"] for x in client.get(ACCOUNTS_URL, headers=a).json()}
    assert account["id"] not in {x["id"] for x in client.get(ACCOUNTS_URL, headers=b).json()}


def test_wrong_content_type_or_broken_json_is_handled(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    response = client.post(
        CATEGORIES_URL,
        content="{not valid json",
        headers={**headers, "Content-Type": "application/json"},
    )
    assert response.status_code == 422
