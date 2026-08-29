FROM python:3.12-slim

# uv: instalador/gestor de pacotes Python rápido, usado em vez de pip puro.
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/

WORKDIR /app

# Copiar só os manifestos primeiro para aproveitar a cache de layers do Docker:
# só volta a correr "uv sync" se pyproject.toml/uv.lock mudarem.
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project

COPY app ./app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
