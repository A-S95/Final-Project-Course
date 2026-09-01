from fastapi.testclient import TestClient

from tests.api.helpers import (
    category_update_body,
    create_account,
    create_category,
    register_and_get_headers,
)

CATEGORIES_URL = "/api/v1/categories"
ACCOUNTS_URL = "/api/v1/accounts"
TRANSACTIONS_URL = "/api/v1/transactions"


def test_create_category(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    body = create_category(client, headers, name="Restaurantes")

    assert body["name"] == "Restaurantes"
    assert body["type"] == "EXPENSE"
    assert body["icon"] is None


def test_register_creates_a_starter_set_of_categories(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    names = {c["name"] for c in client.get(CATEGORIES_URL, headers=headers).json()}

    assert {"Alimentação", "Salário", "Transportes"} <= names


def test_duplicate_name_for_same_user_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    create_category(client, headers, name="Salário", type="INCOME")

    response = client.post(
        CATEGORIES_URL, json={"name": "Salário", "type": "INCOME"}, headers=headers
    )

    assert response.status_code == 409


def test_same_name_allowed_for_different_users(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    create_category(client, headers_a, name="Renda")

    response = client.post(
        CATEGORIES_URL, json={"name": "Renda", "type": "EXPENSE"}, headers=headers_b
    )

    assert response.status_code == 201


def test_list_categories_only_returns_own(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    create_category(client, headers_a, name="Categoria A")
    create_category(client, headers_b, name="Categoria B")

    names = [c["name"] for c in client.get(CATEGORIES_URL, headers=headers_a).json()]

    assert "Categoria A" in names
    assert "Categoria B" not in names


def test_update_category_name(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers)

    response = client.patch(
        f"{CATEGORIES_URL}/{category['id']}",
        json=category_update_body(category, name="Restaurantes"),
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Restaurantes"


def test_update_to_a_name_already_used_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    create_category(client, headers, name="Salário", type="INCOME")
    category = create_category(client, headers, name="Freelance", type="INCOME")

    response = client.patch(
        f"{CATEGORIES_URL}/{category['id']}",
        json=category_update_body(category, name="Salário"),
        headers=headers,
    )

    assert response.status_code == 409


def test_cannot_update_another_users_category(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    category = create_category(client, headers_a)

    response = client.patch(
        f"{CATEGORIES_URL}/{category['id']}",
        json=category_update_body(category, name="Roubada"),
        headers=headers_b,
    )

    assert response.status_code == 404


def test_delete_category(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers, name="Categoria Temporária")

    delete_response = client.delete(f"{CATEGORIES_URL}/{category['id']}", headers=headers)
    assert delete_response.status_code == 204

    remaining = client.get(CATEGORIES_URL, headers=headers).json()
    assert category["id"] not in {c["id"] for c in remaining}


def test_categories_require_authentication(client: TestClient) -> None:
    assert client.get(CATEGORIES_URL).status_code == 401


def test_delete_category_in_use_returns_409(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    category = create_category(client, headers)
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


def test_delete_category_with_reassign_moves_transactions_and_succeeds(
    client: TestClient,
) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers)
    old_category = create_category(client, headers, name="Diversos")
    new_category = create_category(client, headers, name="Alimentação")
    transaction = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": old_category["id"],
            "type": "EXPENSE",
            "amount": "10.00",
            "date": "2026-08-01",
        },
        headers=headers,
    ).json()

    response = client.delete(
        f"{CATEGORIES_URL}/{old_category['id']}",
        params={"reassign_to_category_id": new_category["id"]},
        headers=headers,
    )

    assert response.status_code == 204
    transactions = client.get(TRANSACTIONS_URL, headers=headers).json()
    moved = next(t for t in transactions if t["id"] == transaction["id"])
    assert moved["category_id"] == new_category["id"]
    remaining_categories = client.get(CATEGORIES_URL, headers=headers).json()
    assert old_category["id"] not in {c["id"] for c in remaining_categories}


def test_delete_category_reassign_to_a_different_type_returns_422(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    expense_category = create_category(client, headers, name="Casa", type="EXPENSE")
    income_category = create_category(client, headers, name="Salário", type="INCOME")

    response = client.delete(
        f"{CATEGORIES_URL}/{expense_category['id']}",
        params={"reassign_to_category_id": income_category["id"]},
        headers=headers,
    )

    assert response.status_code == 422


def test_delete_category_reassign_to_itself_returns_422(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers)

    response = client.delete(
        f"{CATEGORIES_URL}/{category['id']}",
        params={"reassign_to_category_id": category["id"]},
        headers=headers,
    )

    assert response.status_code == 422


def test_delete_category_reassign_to_nonexistent_category_returns_422(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    category = create_category(client, headers)

    response = client.delete(
        f"{CATEGORIES_URL}/{category['id']}",
        params={"reassign_to_category_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )

    assert response.status_code == 422
