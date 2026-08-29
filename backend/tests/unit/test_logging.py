import json
import logging

import pytest
from starlette.requests import Request

from app.core.logging import JSONFormatter, error_logger
from app.main import unhandled_exception_handler


def _make_record(**extra: object) -> logging.LogRecord:
    record = logging.LogRecord(
        name="fintrack.errors",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="algo correu mal",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_produces_valid_json_with_expected_fields() -> None:
    record = _make_record(path="/api/v1/auth/login", method="POST", client_host="1.2.3.4")

    payload = json.loads(JSONFormatter().format(record))

    assert payload["level"] == "ERROR"
    assert payload["logger"] == "fintrack.errors"
    assert payload["message"] == "algo correu mal"
    assert payload["path"] == "/api/v1/auth/login"
    assert payload["method"] == "POST"
    assert payload["client_host"] == "1.2.3.4"
    assert "timestamp" in payload


def test_json_formatter_includes_exception_when_present() -> None:
    try:
        raise ValueError("rebentou")
    except ValueError:
        import sys

        record = _make_record()
        record.exc_info = sys.exc_info()

    payload = json.loads(JSONFormatter().format(record))

    assert "ValueError: rebentou" in payload["exception"]


@pytest.mark.asyncio
async def test_unhandled_exception_handler_logs_and_hides_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/boom",
        "client": ("127.0.0.1", 12345),
        "headers": [],
    }
    request = Request(scope)
    exc = ValueError("detalhe interno sensível que não deve chegar ao cliente")

    with caplog.at_level(logging.ERROR, logger="fintrack.errors"):
        response = await unhandled_exception_handler(request, exc)

    assert response.status_code == 500
    body = json.loads(bytes(response.body))
    assert body == {"detail": "Erro interno do servidor."}
    assert b"detalhe interno sens" not in response.body

    assert any(r.name == error_logger.name for r in caplog.records)
    logged = next(r for r in caplog.records if r.name == error_logger.name)
    assert logged.path == "/api/v1/boom"
    assert logged.method == "GET"
