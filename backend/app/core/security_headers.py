from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.core.config import settings

# Cabeçalhos aplicados a todas as respostas da API. A API só devolve JSON (e o
# recibo de uma transação), nunca HTML navegável, por isso a CSP relevante é só a
# que impede embutir a resposta num frame — o resto da CSP (script-src, etc.) vive
# no frontend (ver frontend/vercel.json).
_STATIC_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
}

# HSTS só em produção: em localhost (http) forçaria o browser a tentar https e
# partia o desenvolvimento. 2 anos + includeSubDomains é o valor recomendado.
_HSTS = "max-age=63072000; includeSubDomains"


async def security_headers_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    for header, value in _STATIC_HEADERS.items():
        response.headers.setdefault(header, value)
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", _HSTS)
    return response
