from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"
# Cookie restrito ao path de auth: só é enviado para /refresh e /logout,
# nunca nos outros pedidos à API (o access token é que vai no header Authorization).
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        # `is_production` (não uma comparação direta a "development"): trata
        # "test" da mesma forma que "development"/"local" — sem isto, o cookie
        # ficava `Secure` sob `ENVIRONMENT=test` (como o CI define para o job
        # `test-backend`) e o `TestClient`, que corre sobre http simulado sem
        # TLS, deixava de o reenviar em pedidos seguintes — os testes de
        # rotação de refresh token apanhavam sempre 401 nesse ambiente.
        secure=settings.is_production,
        # "none" em produção: frontend (Vercel) e backend (Render) vivem em
        # domínios diferentes, e um cookie "lax" nunca é enviado em pedidos
        # entre sites diferentes (só entre portas do mesmo site, como em dev
        # local — daí isto nunca ter aparecido antes). "none" exige Secure,
        # por isso só em produção, a par do `secure` acima.
        samesite="none" if settings.is_production else "lax",
        path=REFRESH_COOKIE_PATH,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register(
    request: Request, payload: RegisterRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    try:
        user, access_token, refresh_token = auth_service.register_user(
            db, email=payload.email, password=payload.password, name=payload.name
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Já existe uma conta com este email."
        ) from exc

    db.commit()
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(
    request: Request, payload: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    try:
        user, access_token, refresh_token = auth_service.authenticate(
            db, email=payload.email, password=payload.password
        )
    except InvalidCredentialsError as exc:
        # Mensagem genérica de propósito: não revelar se foi o email ou a
        # password que estava errada (evita enumeração de contas registadas).
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou password inválidos.") from exc

    db.commit()
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
) -> TokenResponse:
    if refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sem refresh token.")

    try:
        user, access_token, new_refresh_token = auth_service.refresh_tokens(
            db, refresh_token=refresh_token
        )
    except InvalidRefreshTokenError as exc:
        # Se a deteção de reutilização revogou toda a família de tokens, isso tem
        # de ficar persistido — daí o commit também no caminho de erro.
        db.commit()
        _clear_refresh_cookie(response)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Refresh token inválido ou expirado."
        ) from exc

    db.commit()
    _set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
) -> None:
    if refresh_token is not None:
        auth_service.logout(db, refresh_token=refresh_token)
        db.commit()
    _clear_refresh_cookie(response)
