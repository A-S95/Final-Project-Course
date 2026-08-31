from fastapi.testclient import TestClient


def test_security_headers_present_on_every_response(client: TestClient) -> None:
    response = client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]


def test_hsts_absent_outside_production(client: TestClient) -> None:
    # ENVIRONMENT=test não é produção — o HSTS forçaria https e partiria o dev/testes.
    response = client.get("/health")
    assert "Strict-Transport-Security" not in response.headers


def test_security_headers_on_error_responses(client: TestClient) -> None:
    # Uma rota inexistente continua a devolver os cabeçalhos.
    response = client.get("/api/v1/nao-existe")
    assert response.status_code == 404
    assert response.headers["X-Content-Type-Options"] == "nosniff"
