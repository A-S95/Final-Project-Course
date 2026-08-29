import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

# Requisito da secção 3 do ARCHITECTURE.md ("observabilidade mínima"): logging
# estruturado de erros, sem puxar uma stack de observability completa (ex:
# structlog, Sentry) para uma app pessoal de baixo tráfego. JSON em stdout é
# suficiente para ser lido/filtrado por qualquer agregador de logs, incluindo
# `docker compose logs`.

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

    Chamado uma vez no arranque da app (`main.py`). Idempotente — pode ser
    chamado outra vez (ex: em testes) sem duplicar handlers.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


# Logger dedicado para erros da aplicação (exceções não tratadas, falhas de
# tarefas de fundo) — separado dos loggers do uvicorn/sqlalchemy para ser
# fácil de filtrar (`logger == "fintrack.errors"`).
error_logger = logging.getLogger("fintrack.errors")
