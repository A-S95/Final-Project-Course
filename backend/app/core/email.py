import json
import urllib.error
import urllib.request

from app.core.config import settings
from app.core.logging import error_logger

_RESEND_ENDPOINT = "https://api.resend.com/emails"


def send_email(*, to: str, subject: str, html: str) -> None:
    """Envia um email transacional.

    Sem `RESEND_API_KEY` (desenvolvimento e testes) o conteúdo é escrito no log em
    vez de enviado — o fluxo de recuperação de password funciona localmente sem
    configurar nada, basta ler o link nos logs do backend.
    """
    if not settings.resend_api_key:
        error_logger.info("Email (modo consola) para %s | assunto: %s\n%s", to, subject, html)
        return

    payload = json.dumps(
        {"from": settings.resend_from_email, "to": [to], "subject": subject, "html": html}
    ).encode("utf-8")
    request = urllib.request.Request(
        _RESEND_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        # Um email que falha não deve rebentar o pedido do utilizador: regista e segue.
        error_logger.error("Falha ao enviar email para %s: %s", to, exc)


def password_reset_email_html(*, name: str, reset_url: str, expire_minutes: int) -> str:
    return f"""\
<div style="font-family: system-ui, sans-serif; color: #1a1a1a; line-height: 1.5;">
  <p>Olá {name},</p>
  <p>Recebemos um pedido para repor a password da tua conta CentiSible.
     Clica no botão abaixo para escolher uma password nova:</p>
  <p style="margin: 24px 0;">
    <a href="{reset_url}"
       style="background: #1f7a4c; color: #fff; padding: 12px 20px; border-radius: 8px;
              text-decoration: none; font-weight: 600;">Repor password</a>
  </p>
  <p style="color: #666; font-size: 14px;">
    Esta ligação expira dentro de {expire_minutes} minutos e só pode ser usada uma vez.
    Se não foste tu a pedir isto, ignora este email — a tua password continua igual.
  </p>
  <p style="color: #666; font-size: 14px;">
    Se o botão não funcionar, copia este endereço:<br>{reset_url}
  </p>
</div>"""
