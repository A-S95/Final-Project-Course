import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.api.helpers import create_account, create_category, register_and_get_headers

TRANSACTIONS_URL = "/api/v1/transactions"


@pytest.fixture(autouse=True)
def _isolated_uploads_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Sem isto, os testes escreviam recibos a sério em backend/uploads/ —
    # cada teste fica com o seu próprio diretório temporário, limpo pelo pytest.
    monkeypatch.setattr(settings, "uploads_dir", str(tmp_path))


def _make_transaction(client: TestClient, headers: dict) -> dict:
    account = create_account(client, headers)
    category = create_category(client, headers, type="EXPENSE")
    response = client.post(
        TRANSACTIONS_URL,
        json={
            "account_id": account["id"],
            "category_id": category["id"],
            "type": "EXPENSE",
            "amount": "12.50",
            "date": "2026-08-10",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _png_file() -> tuple[str, io.BytesIO, str]:
    # Cabeçalho PNG mínimo válido — não precisa de ser uma imagem completa,
    # o backend só guarda os bytes e confia no Content-Type declarado.
    content = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    return ("recibo.png", io.BytesIO(content), "image/png")


def test_transaction_starts_without_receipt(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)

    assert transaction["receipt_content_type"] is None


def test_upload_and_download_receipt(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)
    name, content, content_type = _png_file()

    upload = client.post(
        f"{TRANSACTIONS_URL}/{transaction['id']}/receipt",
        files={"file": (name, content, content_type)},
        headers=headers,
    )
    assert upload.status_code == 200
    assert upload.json()["receipt_content_type"] == "image/png"

    download = client.get(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt", headers=headers)
    assert download.status_code == 200
    assert download.headers["content-type"] == "image/png"
    assert download.content.startswith(b"\x89PNG")


def test_upload_rejects_unsupported_content_type(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)

    response = client.post(
        f"{TRANSACTIONS_URL}/{transaction['id']}/receipt",
        files={"file": ("script.exe", io.BytesIO(b"MZ"), "application/x-msdownload")},
        headers=headers,
    )

    assert response.status_code == 422


def test_upload_rejects_oversized_file(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)
    too_big = io.BytesIO(b"0" * (8 * 1024 * 1024 + 1))

    response = client.post(
        f"{TRANSACTIONS_URL}/{transaction['id']}/receipt",
        files={"file": ("recibo.png", too_big, "image/png")},
        headers=headers,
    )

    assert response.status_code == 422


def test_download_without_receipt_returns_404(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)

    response = client.get(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt", headers=headers)

    assert response.status_code == 404


def test_delete_receipt(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)
    name, content, content_type = _png_file()
    client.post(
        f"{TRANSACTIONS_URL}/{transaction['id']}/receipt",
        files={"file": (name, content, content_type)},
        headers=headers,
    )

    delete = client.delete(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt", headers=headers)
    assert delete.status_code == 200
    assert delete.json()["receipt_content_type"] is None

    download = client.get(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt", headers=headers)
    assert download.status_code == 404


def test_delete_receipt_when_none_attached_returns_404(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)

    response = client.delete(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt", headers=headers)

    assert response.status_code == 404


def test_deleting_transaction_removes_receipt_file(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)
    name, content, content_type = _png_file()
    client.post(
        f"{TRANSACTIONS_URL}/{transaction['id']}/receipt",
        files={"file": (name, content, content_type)},
        headers=headers,
    )

    delete = client.delete(f"{TRANSACTIONS_URL}/{transaction['id']}", headers=headers)
    assert delete.status_code == 204


def test_cannot_access_another_users_receipt(client: TestClient) -> None:
    headers_a = register_and_get_headers(client, email="a@example.com")
    headers_b = register_and_get_headers(client, email="b@example.com")
    transaction = _make_transaction(client, headers_a)
    name, content, content_type = _png_file()
    client.post(
        f"{TRANSACTIONS_URL}/{transaction['id']}/receipt",
        files={"file": (name, content, content_type)},
        headers=headers_a,
    )

    response = client.get(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt", headers=headers_b)

    assert response.status_code == 404


def test_receipt_endpoints_require_authentication(client: TestClient) -> None:
    headers = register_and_get_headers(client)
    transaction = _make_transaction(client, headers)

    assert client.get(f"{TRANSACTIONS_URL}/{transaction['id']}/receipt").status_code == 401
