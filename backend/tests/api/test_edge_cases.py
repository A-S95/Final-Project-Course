"""Casos-limite do domínio que valem a pena fixar num teste: FKs em campos menos
óbvios, aritmética de datas nas fronteiras, e conversões de tipo com invariantes
cruzadas.
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
TRANSACTIONS_URL = "/api/v1/transactions"
DASHBOARD_URL = "/api/v1/dashboard"
HOUSEHOLDS_URL = "/api/v1/households"


def _balance(client: TestClient, headers: dict, account_id: str) -> str:
    accounts = client.get(ACCOUNTS_URL, headers=headers).json()
    return next(a["current_balance"] for a in accounts if a["id"] == account_id)


def test_cannot_delete_the_destination_account_of_a_transfer(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    origin = create_account(client, headers, name="Origem", initial_balance="500.00")
    destination = create_account(client, headers, name="Destino", initial_balance="0.00")
    client.post(
        TRANSACTIONS_URL,
        json={"account_id": origin["id"], "destination_account_id": destination["id"],
              "type": "TRANSFER", "amount": "100.00", "date": "2026-08-01"},
        headers=headers,
    )

    # A conta de destino também está protegida pela FK, não só a de origem.
    assert client.delete(f"{ACCOUNTS_URL}/{destination['id']}", headers=headers).status_code == 409


def test_transaction_in_a_far_future_month_lands_in_that_month(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    category = create_category(client, headers, name="Casa", type="EXPENSE")

    response = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "40.00", "date": "2030-12-25"},
        headers=headers,
    )
    assert response.status_code == 201

    # Não aparece no mês atual...
    now = client.get(DASHBOARD_URL, headers=headers).json()
    assert now["total_expenses"] == "0.00"
    # ...mas aparece em dezembro de 2030 (aritmética de mês na fronteira do ano).
    december = client.get(DASHBOARD_URL, params={"month": "2030-12-01"}, headers=headers).json()
    assert december["total_expenses"] == "40.00"
    # O saldo global (estado "agora") já reflete a transação.
    assert _balance(client, headers, account["id"]) == "-40.00"


def test_converting_an_expense_into_a_transfer_clears_the_category(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account_a = create_account(client, headers, name="A", initial_balance="200.00")
    account_b = create_account(client, headers, name="B", initial_balance="0.00")
    category = create_category(client, headers, type="EXPENSE")
    tx = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account_a["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "50.00", "date": "2026-08-01"},
        headers=headers,
    ).json()
    assert _balance(client, headers, account_a["id"]) == "150.00"

    # EXPENSE -> TRANSFER: tem de limpar a categoria e preencher a conta de destino.
    updated = client.patch(
        f"{TRANSACTIONS_URL}/{tx['id']}",
        json={"account_id": account_a["id"], "destination_account_id": account_b["id"],
              "type": "TRANSFER", "amount": "50.00", "date": "2026-08-01"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["category_id"] is None
    assert updated.json()["destination_account_id"] == account_b["id"]
    # A despesa (−50 em A) foi desfeita e a transferência aplicada (−50 em A, +50 em B):
    # A continua em 150 (a saída passou de "despesa" a "transferência"), B fica com 50.
    assert _balance(client, headers, account_a["id"]) == "150.00"
    assert _balance(client, headers, account_b["id"]) == "50.00"


def test_transfer_missing_destination_account_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    response = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account["id"], "type": "TRANSFER", "amount": "10.00",
              "date": "2026-08-01"},
        headers=headers,
    )
    assert response.status_code == 422


def test_last_member_leaving_a_household_drops_its_pending_invites(client: TestClient) -> None:
    a = register(client, email="a@example.com")
    b = register(client, email="b@example.com")
    ha, hb = auth_headers(a["access_token"]), auth_headers(b["access_token"])
    client.post(HOUSEHOLDS_URL, json={"name": "Casa A"}, headers=ha)
    client.post(f"{HOUSEHOLDS_URL}/me/invites", json={"email": "b@example.com"}, headers=ha)

    # B tem um convite pendente.
    assert len(client.get(f"{HOUSEHOLDS_URL}/invites", headers=hb).json()) == 1

    # A (último membro) sai -> o agregado é apagado e o convite vai em cascata.
    assert client.post(f"{HOUSEHOLDS_URL}/me/leave", headers=ha).status_code == 204
    assert client.get(f"{HOUSEHOLDS_URL}/invites", headers=hb).json() == []


def test_dashboard_month_param_accepts_any_day_of_the_month(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="0.00")
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        TRANSACTIONS_URL,
        json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "12.00", "date": "2026-02-28"},
        headers=headers,
    )
    for day in ("2026-02-01", "2026-02-14", "2026-02-28"):
        body = client.get(DASHBOARD_URL, params={"month": day}, headers=headers).json()
        assert body["month"] == "2026-02-01"
        assert body["total_expenses"] == "12.00"
