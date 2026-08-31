from datetime import date, timedelta

from fastapi.testclient import TestClient

from tests.api.helpers import goal_update_body, register_and_get_headers

GOALS_URL = "/api/v1/goals"


def _create(client: TestClient, headers: dict, **overrides):
    payload = {"name": "Fundo de emergência", "target_amount": "1000.00", **overrides}
    return client.post(GOALS_URL, json=payload, headers=headers)


def test_create_minimal_goal(client: TestClient) -> None:
    headers = register_and_get_headers(client)

    response = _create(client, headers)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Fundo de emergência"
    assert body["current_amount"] == "0.00"
    assert body["remaining"] == "1000.00"
    assert body["progress_percentage"] == 0.0
    assert body["is_achieved"] is False
    assert body["deadline"] is None
    assert body["deadline_passed"] is False
    assert body["months_until_deadline"] is None
    assert body["required_monthly_contribution"] is None


def test_goal_target_must_be_positive(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    assert _create(client, headers, target_amount="0").status_code == 422


def test_required_monthly_contribution_with_deadline(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    deadline = (date.today() + timedelta(days=90)).isoformat()  # ~3 meses

    body = _create(
        client, headers, target_amount="900.00", current_amount="0.00", deadline=deadline
    ).json()

    assert body["months_until_deadline"] == 3
    assert body["required_monthly_contribution"] == "300.00"
    assert body["progress_percentage"] == 0.0


def test_required_monthly_rounds_up(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    deadline = (date.today() + timedelta(days=90)).isoformat()  # 3 meses

    body = _create(
        client, headers, target_amount="1000.00", current_amount="0.00", deadline=deadline
    ).json()

    # 1000 / 3 = 333.33... -> arredonda para cima para garantir que atinge o alvo.
    assert body["required_monthly_contribution"] == "333.34"


def test_achieved_goal_has_no_required_contribution(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    deadline = (date.today() + timedelta(days=90)).isoformat()

    body = _create(
        client, headers, target_amount="500.00", current_amount="500.00", deadline=deadline
    ).json()

    assert body["is_achieved"] is True
    assert body["remaining"] == "0.00"
    assert body["required_monthly_contribution"] is None
    assert body["deadline_passed"] is False


def test_passed_deadline_is_flagged(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    past = (date.today() - timedelta(days=10)).isoformat()

    body = _create(client, headers, current_amount="100.00", deadline=past).json()

    assert body["deadline_passed"] is True
    assert body["required_monthly_contribution"] is None


def test_contribute_adds_to_current_amount(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    goal = _create(client, headers, target_amount="1000.00").json()

    response = client.post(
        f"{GOALS_URL}/{goal['id']}/contributions", json={"amount": "250.00"}, headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_amount"] == "250.00"
    assert body["remaining"] == "750.00"
    assert body["progress_percentage"] == 25.0


def test_contribute_can_reach_the_goal(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    goal = _create(client, headers, target_amount="200.00", current_amount="150.00").json()

    body = client.post(
        f"{GOALS_URL}/{goal['id']}/contributions", json={"amount": "60.00"}, headers=headers
    ).json()

    assert body["current_amount"] == "210.00"
    assert body["is_achieved"] is True
    assert body["remaining"] == "0.00"


def test_contribute_cannot_go_negative(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    goal = _create(client, headers, current_amount="100.00").json()

    response = client.post(
        f"{GOALS_URL}/{goal['id']}/contributions", json={"amount": "-150.00"}, headers=headers
    )

    assert response.status_code == 422


def test_update_goal_fields(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    goal = _create(client, headers).json()

    response = client.patch(
        f"{GOALS_URL}/{goal['id']}",
        json=goal_update_body(
            goal, name="Carro novo", target_amount="8000.00", current_amount="2000.00"
        ),
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Carro novo"
    assert body["target_amount"] == "8000.00"
    assert body["current_amount"] == "2000.00"
    assert body["remaining"] == "6000.00"


def test_update_can_clear_the_deadline(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    deadline = (date.today() + timedelta(days=60)).isoformat()
    goal = _create(client, headers, deadline=deadline).json()
    assert goal["deadline"] == deadline

    cleared = client.patch(
        f"{GOALS_URL}/{goal['id']}",
        json=goal_update_body(goal, deadline=None),
        headers=headers,
    ).json()
    assert cleared["deadline"] is None
    assert cleared["required_monthly_contribution"] is None

    # Um PATCH seguinte que reenvia `deadline: null` mantém-no limpo.
    kept = client.patch(
        f"{GOALS_URL}/{goal['id']}",
        json=goal_update_body(cleared, name="Outro nome"),
        headers=headers,
    ).json()
    assert kept["deadline"] is None


def test_delete_goal(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    goal = _create(client, headers).json()

    assert client.delete(f"{GOALS_URL}/{goal['id']}", headers=headers).status_code == 204
    assert client.get(GOALS_URL, headers=headers).json() == []


def test_goals_are_isolated_per_user(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    goal = _create(client, headers_a).json()

    assert client.get(GOALS_URL, headers=headers_b).json() == []
    assert client.patch(
        f"{GOALS_URL}/{goal['id']}", json=goal_update_body(goal, name="x"), headers=headers_b
    ).status_code == 404
    assert client.post(
        f"{GOALS_URL}/{goal['id']}/contributions", json={"amount": "1"}, headers=headers_b
    ).status_code == 404


def test_goals_require_authentication(client: TestClient) -> None:
    assert client.get(GOALS_URL).status_code == 401
