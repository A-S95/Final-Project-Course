"""SQL injection — o projeto usa sempre o ORM do SQLAlchemy com queries
parametrizadas (`select().where(Coluna == valor)`), nunca concatenação de strings
SQL. Estes testes provam que payloads de injeção são tratados como *dados*: são
guardados/devolvidos literalmente, nunca executados, e a base de dados fica intacta.
"""

from fastapi.testclient import TestClient

from tests.api.helpers import create_account, create_category, register_and_get_headers

SQLI_PAYLOADS = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "1); DELETE FROM accounts WHERE ('1'='1",
    "Robert'); DROP TABLE categories;--",
    '" OR ""="',
    "admin'--",
    "' UNION SELECT email, password_hash, name, currency, monthly_income FROM users --",
    "x'||(SELECT password_hash FROM users LIMIT 1)||'x",
    "%27%20OR%201%3D1",
]

CATEGORIES_URL = "/api/v1/categories"
ACCOUNTS_URL = "/api/v1/accounts"
TRANSACTIONS_URL = "/api/v1/transactions"
GOALS_URL = "/api/v1/goals"
HOUSEHOLDS_URL = "/api/v1/households"


def test_sqli_in_category_name_is_stored_as_literal(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    create_category(client, headers, name="CANARY", type="EXPENSE")

    for payload in SQLI_PAYLOADS:
        response = client.post(
            CATEGORIES_URL, json={"name": payload, "type": "EXPENSE"}, headers=headers
        )
        assert response.status_code == 201, (payload, response.text)
        assert response.json()["name"] == payload  # devolvido tal e qual

    listed = client.get(CATEGORIES_URL, headers=headers).json()
    names = {c["name"] for c in listed}
    assert "CANARY" in names  # nada foi apagado
    assert {"CANARY", *SQLI_PAYLOADS} <= names


def test_sqli_in_account_name_is_stored_as_literal(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    for payload in SQLI_PAYLOADS:
        response = client.post(
            ACCOUNTS_URL,
            json={"name": payload, "type": "BANK", "initial_balance": "10.00"},
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["name"] == payload
    assert len(client.get(ACCOUNTS_URL, headers=headers).json()) == len(SQLI_PAYLOADS)


def test_sqli_in_transaction_description_is_stored_as_literal(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    account = create_account(client, headers, initial_balance="1000.00")
    category = create_category(client, headers, type="EXPENSE")

    payload = "'; DROP TABLE transactions; --"
    response = client.post(
        TRANSACTIONS_URL,
        json={"account_id": account["id"], "category_id": category["id"], "type": "EXPENSE",
              "amount": "10.00", "description": payload, "date": "2026-08-01"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["description"] == payload
    # A tabela continua a funcionar.
    assert client.get(TRANSACTIONS_URL, headers=headers).status_code == 200


def test_sqli_in_goal_and_household_names(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    payload = "Robert'); DROP TABLE goals;--"

    goal = client.post(
        GOALS_URL, json={"name": payload, "target_amount": "100.00"}, headers=headers
    )
    assert goal.status_code == 201
    assert goal.json()["name"] == payload

    household = client.post(HOUSEHOLDS_URL, json={"name": payload}, headers=headers)
    assert household.status_code == 201
    assert household.json()["name"] == payload


def test_sqli_in_login_email_is_rejected_or_unauthorized(client: TestClient) -> None:
    register_and_get_headers(client, email="victim@example.com")
    for payload in ["' OR '1'='1", "victim@example.com'--", "' OR 1=1 --"]:
        response = client.post(
            "/api/v1/auth/login", json={"email": payload, "password": "whatever"}
        )
        # EmailStr rejeita (422) ou credenciais inválidas (401) — nunca 200/500.
        assert response.status_code in (401, 422), (payload, response.status_code)


def test_sqli_in_query_filters_is_rejected(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    # Tipos fortes nos parâmetros (enum, UUID, date) -> 422, nunca executado.
    assert client.get(
        TRANSACTIONS_URL, params={"type": "' OR 1=1"}, headers=headers
    ).status_code == 422
    assert client.get(
        TRANSACTIONS_URL, params={"account_id": "1 OR 1=1"}, headers=headers
    ).status_code == 422
    assert client.get(
        TRANSACTIONS_URL, params={"date_from": "2026-01-01'; DROP TABLE transactions;--"},
        headers=headers,
    ).status_code == 422
    assert client.get(
        "/api/v1/dashboard", params={"scope": "individual' OR '1'='1"}, headers=headers
    ).status_code == 422


def test_union_based_exfiltration_does_not_leak_password_hashes(client: TestClient) -> None:
    headers = register_and_get_headers(client, email="target@example.com")
    payload = (
        "' UNION SELECT email, password_hash, name, currency, monthly_income FROM users --"
    )
    created = client.post(
        CATEGORIES_URL, json={"name": payload, "type": "EXPENSE"}, headers=headers
    )

    # A query UNION não foi executada: o payload ficou guardado como o NOME literal
    # da categoria, e a resposta só tem a categoria (uma linha), sem hashes bcrypt.
    assert created.json()["name"] == payload
    listed = client.get(CATEGORIES_URL, headers=headers).json()
    assert payload in {c["name"] for c in listed}  # guardado como nome literal
    assert "$2b$" not in client.get(CATEGORIES_URL, headers=headers).text


def test_database_survives_a_barrage_of_injection_attempts(client: TestClient) -> None:
    headers = register_and_get_headers(client, email="survivor@example.com")
    for payload in SQLI_PAYLOADS:
        client.post(CATEGORIES_URL, json={"name": payload, "type": "EXPENSE"}, headers=headers)
        client.post(
            ACCOUNTS_URL,
            json={"name": payload, "type": "OTHER", "initial_balance": "0.00"},
            headers=headers,
        )

    # A app continua totalmente funcional: novo registo + login + rota protegida.
    fresh = register_and_get_headers(client, email="after@example.com")
    assert client.get("/api/v1/users/me", headers=fresh).status_code == 200
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "survivor@example.com", "password": "correct horse battery staple"},
        ).status_code
        == 200
    )
