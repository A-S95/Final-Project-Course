import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

# JSON em stdout: suficiente para filtrar com `docker compose logs`, sem stack
# de observability completa (structlog/Sentry) para uma app de baixo tráfego.

_EXTRA_FIELDS = ("path", "method", "client_host", "user_id")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """Substitui os handlers da root logger por um único handler JSON em stdout.
    Idempotente — pode ser chamado outra vez (ex: em testes) sem duplicar handlers."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


# Separado dos loggers do uvicorn/sqlalchemy para filtrar por `logger == "fintrack.errors"`.
error_logger = logging.getLogger("fintrack.errors")
