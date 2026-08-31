from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import password_reset_email_html, send_email
from app.core.exceptions import InvalidRefreshTokenError, RefreshTokenRaceError
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"
# Só enviado para /refresh e /logout — o access token vai no header Authorization.
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        # `is_production` (não só "development"): mantém o cookie sem Secure em
        # ENVIRONMENT=test, senão o TestClient (http simulado) deixa de o reenviar.
        secure=settings.is_production,
        # "none" só em produção: frontend (Vercel) e backend (Render) são domínios
        # diferentes, e "lax" nunca é enviado entre sites diferentes. "none" exige Secure.
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
    user, access_token, refresh_token = auth_service.register_user(
        db, email=payload.email, password=payload.password, name=payload.name
    )
    db.commit()
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(
    request: Request, payload: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    # InvalidCredentialsError → 401 "Email ou password inválidos." (mensagem genérica
    # de propósito, evita enumeração de contas) via o handler em main.py.
    user, access_token, refresh_token = auth_service.authenticate(
        db, email=payload.email, password=payload.password
    )
    db.commit()
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/hour")
def password_reset_request(
    request: Request,
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    result = auth_service.request_password_reset(db, email=payload.email)
    db.commit()
    if result is not None:
        user, raw_token = result
        reset_url = f"{settings.frontend_base_url}/redefinir-password?token={raw_token}"
        # Enviar o email depois da resposta: o cliente não fica à espera do
        # round-trip à Resend (que já era lento, e ainda mais com a Render a acordar).
        background_tasks.add_task(
            send_email,
            to=user.email,
            subject="Repor a tua password — CentiSible",
            html=password_reset_email_html(
                name=user.name,
                reset_url=reset_url,
                expire_minutes=settings.password_reset_token_expire_minutes,
            ),
        )
    # Resposta igual exista ou não a conta — não revela que emails estão registados.
    return {"detail": "Se existir uma conta com esse email, enviámos as instruções."}


@router.post("/password-reset/confirm")
@limiter.limit("10/hour")
def password_reset_confirm(
    request: Request,
    payload: PasswordResetConfirm,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    # InvalidPasswordResetTokenError → 400 via o handler em main.py.
    auth_service.reset_password(db, token=payload.token, new_password=payload.password)
    db.commit()
    _clear_refresh_cookie(response)  # a password mudou — todas as sessões terminaram
    return {"detail": "Password alterada. Já podes entrar com a nova."}


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
    except RefreshTokenRaceError as exc:
        # Corrida benigna: NÃO limpar o cookie (o pedido paralelo já o trocou por um
        # novo, e limpá-lo aqui apagava o bom) e NÃO revogar nada. 409: o cliente
        # volta a tentar e apanha o cookie novo.
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Sessão a ser renovada noutro pedido — tenta novamente."
        ) from exc
    except InvalidRefreshTokenError as exc:
        # Commit também aqui: uma reutilização detetada já revogou tokens na BD.
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
