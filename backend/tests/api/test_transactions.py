from fastapi.testclient import TestClient

from tests.api.helpers import create_account, create_category, register_and_get_headers

ACCOUNTS_URL = "/api/v1/accounts"
CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"


def _get_account(client: TestClient, headers: dict, account_id: str) -> dict:
    response = client.get(ACCOUNTS_URL, headers=headers)
    return next(a for a in response.json() if a["id"] == account_id)


def test_income_transaction_increases_account_balance(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    category = create_category(client, headers, name="Salário", type="INCOME")

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "INCOME",
            "amount": "500.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 201
    updated_account = _get_account(client, headers, account["id"])
    assert updated_account["current_balance"] == "600.00"


def test_expense_transaction_decreases_account_balance(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    category = create_category(client, headers, name="Alimentação", type="EXPENSE")

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 201
    updated_account = _get_account(client, headers, account["id"])
    assert updated_account["current_balance"] == "70.00"


def test_transfer_moves_balance_between_accounts(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    origin = create_account(client, headers, name="Millennium", initial_balance="100.00")
    destination = create_account(client, headers, name="Revolut", initial_balance="0.00")

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": origin["id"],
            "destination_account_id": destination["id"],
            "type": "TRANSFER",
            "amount": "40.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 201
    updated_origin = _get_account(client, headers, origin["id"])
    updated_destination = _get_account(client, headers, destination["id"])
    assert updated_origin["current_balance"] == "60.00"
    assert updated_destination["current_balance"] == "40.00"


def test_transfer_to_same_account_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "destination_account_id": account["id"],
            "type": "TRANSFER",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_transfer_with_category_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    origin = create_account(client, headers, name="Millennium")
    destination = create_account(client, headers, name="Revolut")
    category = create_category(client, headers)

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": origin["id"],
            "destination_account_id": destination["id"],
            "category_id": category["id"],
            "type": "TRANSFER",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_income_without_category_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "type": "INCOME",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_category_type_mismatch_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    expense_category = create_category(client, headers, name="Alimentação", type="EXPENSE")

    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": expense_category["id"],
            "type": "INCOME",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_update_transaction_amount_adjusts_balance_by_delta(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    category = create_category(client, headers, type="EXPENSE")
    create_response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )
    transaction = create_response.json()

    response = client.patch(
        f"{TRANSACTIONS_URL}/{transaction['id']}",
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "50.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 200
    updated_account = _get_account(client, headers, account["id"])
    assert updated_account["current_balance"] == "50.00"


def test_update_transaction_changing_account_moves_effect_between_accounts(
    client: TestClient,
) -> None:
    headers = register_and_get_headers(client)
    account_a = create_account(client, headers, name="Conta A", initial_balance="100.00")
    account_b = create_account(client, headers, name="Conta B", initial_balance="100.00")
    category = create_category(client, headers, type="EXPENSE")
    create_response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account_a["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )
    transaction = create_response.json()

    response = client.patch(
        f"{TRANSACTIONS_URL}/{transaction['id']}",
        json={
            "account_id": account_b["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert _get_account(client, headers, account_a["id"])["current_balance"] == "100.00"
    assert _get_account(client, headers, account_b["id"])["current_balance"] == "70.00"


def test_delete_transaction_reverts_balance(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")
    category = create_category(client, headers, type="EXPENSE")
    create_response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )
    transaction = create_response.json()

    delete_response = client.delete(
        f"{TRANSACTIONS_URL}/{transaction['id']}", headers=headers
    )

    assert delete_response.status_code == 204
    assert _get_account(client, headers, account["id"])["current_balance"] == "100.00"


def test_list_transactions_filters_by_account_category_type_and_date(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account_a = create_account(client, headers, name="Conta A")
    account_b = create_account(client, headers, name="Conta B")
    food = create_category(client, headers, name="Alimentação", type="EXPENSE")
    salary = create_category(client, headers, name="Salário", type="INCOME")

    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account_a["id"],
            "category_id": food["id"],
            "type": "EXPENSE",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account_b["id"],
            "category_id": salary["id"],
            "type": "INCOME",
            "amount": "1000.00",
            "date": "2026-07-15",
        },
        headers=headers,
    )

    by_account = client.get(
        TRANSACTIONS_URL, params={"account_id": account_a["id"]}, headers=headers
    )
    assert len(by_account.json()) == 1

    by_type = client.get(TRANSACTIONS_URL, params={"type": "INCOME"}, headers=headers)
    assert len(by_type.json()) == 1

    by_category = client.get(TRANSACTIONS_URL, params={"category_id": food["id"]}, headers=headers)
    assert len(by_category.json()) == 1

    by_date = client.get(
        TRANSACTIONS_URL,
        params={"date_from": "2026-08-01", "date_to": "2026-08-31"},
        headers=headers,
    )
    assert len(by_date.json()) == 1


def test_cannot_access_another_users_transaction(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    account = create_account(client, headers_a)
    category = create_category(client, headers_a, type="EXPENSE")
    create_response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers_a,
    )
    transaction = create_response.json()

    delete_response = client.delete(f"{TRANSACTIONS_URL}/{transaction['id']}", headers=headers_b)

    assert delete_response.status_code == 404


def test_deleting_account_with_transactions_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    response = client.delete(f"{ACCOUNTS_URL}/{account['id']}", headers=headers)

    assert response.status_code == 409


def test_deleting_category_with_transactions_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    )

    response = client.delete(f"{CATEGORIES_URL}/{category['id']}", headers=headers)

    assert response.status_code == 409


def test_transactions_require_authentication(client: TestClient) -> None:
    assert client.get(TRANSACTIONS_URL).status_code == 401


def test_export_csv_returns_attachment_with_the_users_transactions(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, name="Conta Principal", initial_balance="0.00")
    category = create_category(client, headers, name="Alimentação", type="EXPENSE")
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "12.34",
            "description": "Café com acentuação: pão",
            "date": "2026-08-10",
        },
        headers=headers,
    )

    response = client.get(f"{TRANSACTIONS_URL}/export", headers=headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert ".csv" in response.headers["content-disposition"]

    body = response.content.decode("utf-8-sig")  # tolera o BOM
    lines = body.splitlines()
    assert lines[0] == "Data;Tipo;Descrição;Valor;Conta;Conta destino;Categoria;Partilhada"
    expected_row = (
        "2026-08-10;Despesa;Café com acentuação: pão;12,34;Conta Principal;;Alimentação;Não"
    )
    assert lines[1] == expected_row


def test_export_csv_only_includes_the_authenticated_users_transactions(client: TestClient) -> None:
    alice = register_and_get_headers(client, email="alice.export@example.com")
    a_account = create_account(client, alice)
    a_category = create_category(client, alice, type="EXPENSE")
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": a_account["id"],
            "category_id": a_category["id"],
            "type": "EXPENSE",
            "amount": "99.00",
            "description": "segredo da alice",
            "date": "2026-08-01",
        },
        headers=alice,
    )

    bob = register_and_get_headers(client, email="bob.export@example.com")
    body = client.get(f"{TRANSACTIONS_URL}/export", headers=bob).content.decode("utf-8-sig")

    assert "segredo da alice" not in body
    assert len(body.splitlines()) == 1  # só o cabeçalho


def test_export_csv_requires_authentication(client: TestClient) -> None:
    assert client.get(f"{TRANSACTIONS_URL}/export").status_code == 401
