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
from app.core.exceptions import DomainError
from app.core.logging import configure_logging, error_logger
from app.core.rate_limit import limiter
from app.core.security_headers import security_headers_middleware
from app.db.session import SessionLocal
from app.repositories import password_reset_token_repository, refresh_token_repository

configure_logging()

# Uma vez por dia chega para manter as tabelas de tokens pequenas, a esta escala.
TOKEN_CLEANUP_INTERVAL_SECONDS = 24 * 60 * 60


def _cleanup_expired_tokens_once() -> None:
    db = SessionLocal()
    try:
        refresh_deleted = refresh_token_repository.delete_expired(db)
        reset_deleted = password_reset_token_repository.delete_expired(db)
        db.commit()
        if refresh_deleted or reset_deleted:
            error_logger.info(
                "Limpeza de tokens: %d refresh + %d reset de password expirados removidos.",
                refresh_deleted,
                reset_deleted,
            )
    except Exception:
        db.rollback()
        error_logger.exception("Falha na limpeza periódica de tokens.")
    finally:
        db.close()


async def _cleanup_expired_tokens_periodically() -> None:
    """Tarefa de fundo: apaga tokens expirados (refresh + reset de password) a cada
    24h, no próprio processo (sem scheduler externo). `asyncio.to_thread` porque o
    trabalho é síncrono (SQLAlchemy síncrono); chamá-lo direto bloquearia o event
    loop inteiro, incluindo `/health`, até a query terminar."""
    while True:
        await asyncio.to_thread(_cleanup_expired_tokens_once)
        await asyncio.sleep(TOKEN_CLEANUP_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_cleanup_expired_tokens_periodically())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title="CentiSible API",
    version="0.1.0",
    description="API da plataforma de gestão de finanças pessoais CentiSible.",
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


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Erro de regra de negócio (4xx esperado) → resposta com o `detail` da exceção.
    Evita repetir `try/except ... raise HTTPException` em cada endpoint."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Rede de segurança: nunca devia disparar, mas se disparar regista estruturado
    # e o cliente nunca vê um stack trace.
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

app.middleware("http")(security_headers_middleware)

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
