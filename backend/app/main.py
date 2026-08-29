import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1 import (
    accounts,
    analytics,
    auth,
    budgets,
    categories,
    dashboard,
    goals,
    households,
    insights,
    recurring_expenses,
    transactions,
    users,
)
from app.core.config import settings
from app.core.logging import configure_logging, error_logger
from app.core.rate_limit import limiter
from app.db.session import SessionLocal
from app.repositories import refresh_token_repository

configure_logging()

# Uma vez por dia é suficiente para uma app pessoal de baixo volume — não é
# preciso mais frequência para manter a tabela `refresh_tokens` pequena.
REFRESH_TOKEN_CLEANUP_INTERVAL_SECONDS = 24 * 60 * 60


async def _cleanup_refresh_tokens_periodically() -> None:
    """Tarefa de fundo: apaga refresh tokens expirados a cada 24h.

    Corre no próprio processo (`asyncio.create_task`, sem scheduler externo
    tipo APScheduler/Celery) — simples o suficiente para não justificar mais
    uma dependência nesta escala de projeto. Limpa uma vez logo no arranque
    (útil sobretudo em dev, onde o processo pode ficar dias sem reiniciar) e
    depois a cada intervalo.
    """
    while True:
        db = SessionLocal()
        try:
            deleted = refresh_token_repository.delete_expired(db)
            db.commit()
            if deleted:
                error_logger.info(
                    "Limpeza de refresh_tokens: %d token(s) expirado(s) removido(s).", deleted
                )
        except Exception:
            db.rollback()
            error_logger.exception("Falha na limpeza periódica de refresh_tokens.")
        finally:
            db.close()
        await asyncio.sleep(REFRESH_TOKEN_CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_cleanup_refresh_tokens_periodically())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title="FinTrack API",
    version="0.1.0",
    description="API da plataforma de gestão de finanças pessoais FinTrack.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiados pedidos. Tenta novamente dentro de instantes."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Rede de segurança para qualquer exceção que escape aos handlers de
    # domínio já existentes em cada rota (ver `app/core/exceptions.py`) — nunca
    # deveria acontecer em funcionamento normal, mas se acontecer isto garante
    # que fica registado de forma estruturada em vez de só aparecer no stdout
    # em texto livre, e que o cliente nunca vê um stack trace.
    error_logger.error(
        "Exceção não tratada em %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_host": request.client.host if request.client else None,
        },
    )
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor."})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(households.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(recurring_expenses.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Endpoint simples para confirmar que a API está de pé e a que ambiente pertence."""
    return {"status": "ok", "environment": settings.environment}
