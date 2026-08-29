from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    # O ambiente reflete `ENVIRONMENT` (ex: "test" no CI, "development" em local)
    # — não pode ser um literal fixo, ou o teste falha sempre que corre num
    # ambiente diferente do da máquina onde foi escrito.
    assert response.json() == {"status": "ok", "environment": settings.environment}
