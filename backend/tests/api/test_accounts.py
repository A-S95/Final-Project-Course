from fastapi.testclient import TestClient

from tests.api.helpers import account_update_body, create_account, register_and_get_headers

ACCOUNTS_URL = "/api/v1/accounts"


def test_create_account_sets_current_balance_to_initial_balance(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    body = create_account(client, headers, initial_balance="250.00")

    assert body["name"] == "Millennium"
    assert body["type"] == "BANK"
    assert body["initial_balance"] == "250.00"
    assert body["current_balance"] == "250.00"


def test_list_accounts_only_returns_own_accounts(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    create_account(client, headers_a, name="Conta A")
    create_account(client, headers_b, name="Conta B")

    response = client.get(ACCOUNTS_URL, headers=headers_a)

    assert response.status_code == 200
    names = [account["name"] for account in response.json()]
    assert names == ["Conta A"]


def test_update_initial_balance_adjusts_current_balance_by_delta(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")

    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}",
        json=account_update_body(account, initial_balance="150.00"),
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["initial_balance"] == "150.00"
    assert body["current_balance"] == "150.00"


def test_update_name_does_not_touch_balances(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="100.00")

    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}",
        json=account_update_body(account, name="Nova Conta"),
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nova Conta"
    assert body["current_balance"] == "100.00"


def test_cannot_update_another_users_account(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    account = create_account(client, headers_a)

    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}",
        json=account_update_body(account, name="Roubada"),
        headers=headers_b,
    )

    assert response.status_code == 404


def test_delete_account(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)

    delete_response = client.delete(f"{ACCOUNTS_URL}/{account['id']}", headers=headers)
    assert delete_response.status_code == 204

    list_response = client.get(ACCOUNTS_URL, headers=headers)
    assert list_response.json() == []


def test_create_account_with_card_fields(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    body = create_account(
        client, headers, name="Universo", type="CREDIT_CARD",
        card_expiration_date="2027-05-31", card_plafond="1000.00",
    )

    assert body["card_expiration_date"] == "2027-05-31"
    assert body["card_plafond"] == "1000.00"


def test_create_account_without_card_fields_defaults_to_null(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    body = create_account(client, headers)

    assert body["card_expiration_date"] is None
    assert body["card_plafond"] is None


def test_update_card_fields(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, type="CREDIT_CARD")

    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}",
        json=account_update_body(
            account, card_expiration_date="2028-01-31", card_plafond="500.00"
        ),
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["card_expiration_date"] == "2028-01-31"
    assert body["card_plafond"] == "500.00"


def test_update_can_clear_card_fields_explicitly(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(
        client, headers, type="CREDIT_CARD",
        card_expiration_date="2028-01-31", card_plafond="500.00",
    )

    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}",
        json=account_update_body(account, card_expiration_date=None, card_plafond=None),
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["card_expiration_date"] is None
    assert body["card_plafond"] is None


def test_update_keeping_card_fields_leaves_them_untouched(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(
        client, headers, type="CREDIT_CARD",
        card_expiration_date="2028-01-31", card_plafond="500.00",
    )

    response = client.patch(
        f"{ACCOUNTS_URL}/{account['id']}",
        json=account_update_body(account, name="Universo renomeado"),
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["card_expiration_date"] == "2028-01-31"
    assert body["card_plafond"] == "500.00"


def test_accounts_require_authentication(client: TestClient) -> None:
    assert client.get(ACCOUNTS_URL).status_code == 401
