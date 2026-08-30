from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    # Não pode ser literal fixo: ENVIRONMENT varia entre CI e máquina local.
    assert response.json() == {"status": "ok", "environment": settings.environment}
