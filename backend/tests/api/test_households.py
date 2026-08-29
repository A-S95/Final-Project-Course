from fastapi.testclient import TestClient

from tests.api.helpers import (
    auth_headers,
    create_account,
    create_category,
    register,
)

HOUSEHOLDS_URL = "/api/v1/households"
TRANSACTIONS_URL = "/api/v1/transactions"
DASHBOARD_URL = "/api/v1/dashboard"


def _make_user(client: TestClient, email: str, name: str = "User") -> dict:
    body = register(client, email=email, name=name)
    return {"headers": auth_headers(body["access_token"]), "user": body["user"]}


def _create_household(client: TestClient, headers: dict, name: str = "Família Santos") -> dict:
    response = client.post(HOUSEHOLDS_URL, json={"name": name}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _invite(client: TestClient, headers: dict, email: str):
    return client.post(f"{HOUSEHOLDS_URL}/me/invites", json={"email": email}, headers=headers)


# --- criar / ver agregado ------------------------------------------------


def test_create_household_makes_creator_a_member(client: TestClient) -> None:
    a = _make_user(client, "a@example.com", "Antonio")

    household = _create_household(client, a["headers"])

    assert household["name"] == "Família Santos"
    assert household["created_by"] == a["user"]["id"]
    assert len(household["members"]) == 1
    assert household["members"][0]["user_id"] == a["user"]["id"]
    assert household["members"][0]["is_creator"] is True


def test_cannot_create_second_household(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _create_household(client, a["headers"])

    response = client.post(HOUSEHOLDS_URL, json={"name": "Outra"}, headers=a["headers"])

    assert response.status_code == 409


def test_get_my_household_404_when_not_in_one(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")

    assert client.get(f"{HOUSEHOLDS_URL}/me", headers=a["headers"]).status_code == 404


# --- convites -----------------------------------------------------------


def test_invite_and_accept_flow(client: TestClient) -> None:
    a = _make_user(client, "a@example.com", "Antonio")
    b = _make_user(client, "b@example.com", "Beatriz")
    _create_household(client, a["headers"])

    invite = _invite(client, a["headers"], "b@example.com")
    assert invite.status_code == 201
    invite_id = invite.json()["id"]
    assert invite.json()["invited_user_name"] == "Beatriz"
    assert invite.json()["status"] == "PENDING"

    received = client.get(f"{HOUSEHOLDS_URL}/invites", headers=b["headers"]).json()
    assert [i["id"] for i in received] == [invite_id]

    accept = client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=b["headers"])
    assert accept.status_code == 200
    assert len(accept.json()["members"]) == 2

    # Agora os dois veem o mesmo agregado.
    a_view = client.get(f"{HOUSEHOLDS_URL}/me", headers=a["headers"]).json()
    b_view = client.get(f"{HOUSEHOLDS_URL}/me", headers=b["headers"]).json()
    assert a_view["id"] == b_view["id"]
    assert {m["user_id"] for m in b_view["members"]} == {a["user"]["id"], b["user"]["id"]}


def test_invite_unknown_email_returns_404(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _create_household(client, a["headers"])

    assert _invite(client, a["headers"], "ninguem@example.com").status_code == 404


def test_invite_requires_being_in_a_household(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _make_user(client, "b@example.com")

    assert _invite(client, a["headers"], "b@example.com").status_code == 404


def test_cannot_invite_yourself(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _create_household(client, a["headers"])

    assert _invite(client, a["headers"], "a@example.com").status_code == 409


def test_cannot_invite_existing_member(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]
    client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=b["headers"])

    assert _invite(client, a["headers"], "b@example.com").status_code == 409


def test_cannot_invite_person_already_in_another_household(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    _create_household(client, a["headers"], name="Casa A")
    _create_household(client, b["headers"], name="Casa B")

    response = _invite(client, a["headers"], "b@example.com")
    assert response.status_code == 409


def test_duplicate_pending_invite_is_rejected(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _make_user(client, "b@example.com")
    _create_household(client, a["headers"])

    assert _invite(client, a["headers"], "b@example.com").status_code == 201
    assert _invite(client, a["headers"], "b@example.com").status_code == 409


def test_decline_invite(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]

    decline = client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/decline", headers=b["headers"])
    assert decline.status_code == 204
    assert client.get(f"{HOUSEHOLDS_URL}/me", headers=b["headers"]).status_code == 404
    # E é possível reconvidar depois de recusado.
    assert _invite(client, a["headers"], "b@example.com").status_code == 201


def test_cancel_sent_invite(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]

    cancel = client.delete(f"{HOUSEHOLDS_URL}/me/invites/{invite_id}", headers=a["headers"])
    assert cancel.status_code == 204
    assert client.get(f"{HOUSEHOLDS_URL}/invites", headers=b["headers"]).json() == []
    assert client.get(f"{HOUSEHOLDS_URL}/me/invites", headers=a["headers"]).json() == []


def test_cannot_accept_invite_meant_for_someone_else(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _make_user(client, "b@example.com")
    c = _make_user(client, "c@example.com")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]

    response = client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=c["headers"])
    assert response.status_code == 404


def test_accepting_second_invite_after_joining_is_rejected(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    c = _make_user(client, "c@example.com")
    _create_household(client, a["headers"], name="Casa A")
    _create_household(client, c["headers"], name="Casa C")

    invite_a = _invite(client, a["headers"], "b@example.com").json()["id"]
    invite_c = _invite(client, c["headers"], "b@example.com").json()["id"]

    assert (
        client.post(f"{HOUSEHOLDS_URL}/invites/{invite_a}/accept", headers=b["headers"]).status_code
        == 200
    )
    # Já pertence ao agregado A — não pode aceitar o de C.
    assert (
        client.post(f"{HOUSEHOLDS_URL}/invites/{invite_c}/accept", headers=b["headers"]).status_code
        == 409
    )
    # E o convite de C foi automaticamente cancelado ao aceitar o de A.
    assert client.get(f"{HOUSEHOLDS_URL}/invites", headers=b["headers"]).json() == []


# --- sair -------------------------------------------------------------


def test_leave_household_removes_membership(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]
    client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=b["headers"])

    leave = client.post(f"{HOUSEHOLDS_URL}/me/leave", headers=b["headers"])
    assert leave.status_code == 204
    assert client.get(f"{HOUSEHOLDS_URL}/me", headers=b["headers"]).status_code == 404
    # O agregado continua a existir para A (ainda tem um membro).
    assert len(client.get(f"{HOUSEHOLDS_URL}/me", headers=a["headers"]).json()["members"]) == 1


def test_last_member_leaving_deletes_the_household(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    _create_household(client, a["headers"])

    assert client.post(f"{HOUSEHOLDS_URL}/me/leave", headers=a["headers"]).status_code == 204
    # Pode voltar a criar um novo do zero.
    recreate = client.post(HOUSEHOLDS_URL, json={"name": "Novo"}, headers=a["headers"])
    assert recreate.status_code == 201


def test_leave_when_not_in_household_returns_404(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    assert client.post(f"{HOUSEHOLDS_URL}/me/leave", headers=a["headers"]).status_code == 404


# --- dashboard em modo agregado -------------------------------------


def test_dashboard_household_scope_aggregates_all_members(client: TestClient) -> None:
    a = _make_user(client, "a@example.com", "Antonio")
    b = _make_user(client, "b@example.com", "Beatriz")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]
    client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=b["headers"])

    acc_a = create_account(client, a["headers"], name="Conta A", initial_balance="100.00")
    acc_b = create_account(client, b["headers"], name="Conta B", initial_balance="50.00")
    cat_a = create_category(client, a["headers"], name="Comida", type="EXPENSE")
    cat_b = create_category(client, b["headers"], name="Comida", type="EXPENSE")

    client.post(
        TRANSACTIONS_URL,
        json={"account_id": acc_a["id"], "category_id": cat_a["id"], "type": "EXPENSE",
              "amount": "40.00", "date": "2026-08-05"},
        headers=a["headers"],
    )
    client.post(
        TRANSACTIONS_URL,
        json={"account_id": acc_b["id"], "category_id": cat_b["id"], "type": "EXPENSE",
              "amount": "25.00", "date": "2026-08-06"},
        headers=b["headers"],
    )

    individual = client.get(
        DASHBOARD_URL, params={"month": "2026-08-01"}, headers=a["headers"]
    ).json()
    assert individual["scope"] == "individual"
    assert individual["total_expenses"] == "40.00"
    assert individual["total_balance"] == "60.00"

    household = client.get(
        DASHBOARD_URL,
        params={"month": "2026-08-01", "scope": "household"},
        headers=a["headers"],
    ).json()
    assert household["scope"] == "household"
    assert household["total_expenses"] == "65.00"
    assert household["total_balance"] == "85.00"
    # As duas categorias "Comida" (uma de cada membro) são despesas pessoais
    # (`is_shared` por omissão é `False`) que só por coincidência têm o mesmo
    # nome — cada uma paga a sua própria comida, não é um custo partilhado.
    # Ficam em duas linhas separadas, uma por pessoa, identificadas por
    # `owner_name` — juntá-las numa só somaria duas despesas independentes
    # como se fossem uma, o que seria enganador (ver
    # test_dashboard_household_merges_shared_expenses_with_same_category_name
    # para o caso em que devem mesmo fundir-se).
    breakdown = household["expenses_by_category"]
    assert {(row["name"], row["owner_name"], row["total"]) for row in breakdown} == {
        ("Comida", "Antonio", "40.00"),
        ("Comida", "Beatriz", "25.00"),
    }


def test_dashboard_household_merges_shared_expenses_with_same_category_name(
    client: TestClient,
) -> None:
    a = _make_user(client, "a@example.com", "Antonio")
    b = _make_user(client, "b@example.com", "Beatriz")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]
    client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=b["headers"])

    acc_a = create_account(client, a["headers"], name="Conta A", initial_balance="0")
    acc_b = create_account(client, b["headers"], name="Conta B", initial_balance="0")
    cat_a = create_category(client, a["headers"], name="Renda", type="EXPENSE")
    cat_b = create_category(client, b["headers"], name="Renda", type="EXPENSE")

    # Os dois pagam metade da mesma renda e marcam-na como partilhada — é um
    # único custo da casa, não duas rendas diferentes.
    for headers, account, category, amount in (
        (a["headers"], acc_a, cat_a, "420.00"),
        (b["headers"], acc_b, cat_b, "420.00"),
    ):
        client.post(
            TRANSACTIONS_URL,
            json={
                "account_id": account["id"],
                "category_id": category["id"],
                "type": "EXPENSE",
                "amount": amount,
                "date": "2026-08-05",
                "is_shared": True,
            },
            headers=headers,
        )
    # Uma despesa pessoal da Beatriz, não partilhada, categoria diferente —
    # só aqui para confirmar que não se mistura com a renda fundida.
    cat_lazer = create_category(client, b["headers"], name="Lazer", type="EXPENSE")
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": acc_b["id"],
            "category_id": cat_lazer["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-06",
            "is_shared": False,
        },
        headers=b["headers"],
    )

    household = client.get(
        DASHBOARD_URL,
        params={"month": "2026-08-01", "scope": "household"},
        headers=a["headers"],
    ).json()

    breakdown = household["expenses_by_category"]
    assert {(row["name"], row["owner_name"], row["total"]) for row in breakdown} == {
        ("Renda", None, "840.00"),
        ("Lazer", "Beatriz", "30.00"),
    }


def test_dashboard_shared_expenses_total_counts_only_is_shared(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")
    b = _make_user(client, "b@example.com")
    _create_household(client, a["headers"])
    invite_id = _invite(client, a["headers"], "b@example.com").json()["id"]
    client.post(f"{HOUSEHOLDS_URL}/invites/{invite_id}/accept", headers=b["headers"])

    acc_a = create_account(client, a["headers"], name="Conta A", initial_balance="0")
    acc_b = create_account(client, b["headers"], name="Conta B", initial_balance="0")
    cat_a = create_category(client, a["headers"], name="Renda", type="EXPENSE")
    cat_b = create_category(client, b["headers"], name="Lazer", type="EXPENSE")

    # Antonio paga a renda toda e marca-a como partilhada — a Teresa não
    # precisa de lançar a sua própria "Renda" duplicada.
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": acc_a["id"],
            "category_id": cat_a["id"],
            "type": "EXPENSE",
            "amount": "800.00",
            "date": "2026-08-05",
            "is_shared": True,
        },
        headers=a["headers"],
    )
    # Uma despesa pessoal da Teresa, não partilhada.
    client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": acc_b["id"],
            "category_id": cat_b["id"],
            "type": "EXPENSE",
            "amount": "30.00",
            "date": "2026-08-06",
            "is_shared": False,
        },
        headers=b["headers"],
    )

    household = client.get(
        DASHBOARD_URL,
        params={"month": "2026-08-01", "scope": "household"},
        headers=a["headers"],
    ).json()

    assert household["total_expenses"] == "830.00"
    assert household["shared_expenses_total"] == "800.00"


def test_dashboard_household_scope_falls_back_when_not_in_a_household(client: TestClient) -> None:
    a = _make_user(client, "a@example.com")

    body = client.get(
        DASHBOARD_URL, params={"scope": "household"}, headers=a["headers"]
    ).json()

    assert body["scope"] == "individual"


def test_households_require_authentication(client: TestClient) -> None:
    assert client.get(f"{HOUSEHOLDS_URL}/me").status_code == 401
    assert client.get(f"{HOUSEHOLDS_URL}/invites").status_code == 401
