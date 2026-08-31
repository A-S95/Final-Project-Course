from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Substrings que denunciam um SECRET_KEY que ficou por trocar.
_PLACEHOLDER_MARKERS = ("change", "example", "placeholder", "your-secret", "todo")


class Settings(BaseSettings):
    """Configuração da aplicação, carregada de variáveis de ambiente / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str

    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    # Reutilizar um refresh token já rodado dentro desta janela trata-se como uma
    # corrida benigna (mesmo cookie enviado 2x quase ao mesmo tempo: PWA + aba do
    # browser, F5 durante um pedido lento, retry de rede), não como roubo. Só
    # falha esse pedido; a família de tokens fica intacta. Reutilização depois
    # da janela continua a revogar toda a família (ver auth_service.refresh_tokens).
    refresh_reuse_grace_seconds: int = 10

    uploads_dir: str = "uploads"  # relativo ao cwd; ver volume uploads_data no compose

    # Recuperação de password. Sem RESEND_API_KEY o email é escrito no log em vez
    # de enviado (dev/testes funcionam sem configurar nada — ver app/core/email.py).
    resend_api_key: str = ""
    resend_from_email: str = "CentiSible <onboarding@resend.dev>"
    frontend_base_url: str = "http://localhost:5173"
    password_reset_token_expire_minutes: int = 60

    @property
    def is_production(self) -> bool:
        return self.environment.lower() not in ("development", "dev", "local", "test")

    @field_validator("secret_key")
    @classmethod
    def _secret_key_long_enough(cls, value: str) -> str:
        # 32 caracteres é o mínimo recomendado pela RFC 7518 para HMAC-SHA256.
        if len(value) < 32:
            raise ValueError(
                "SECRET_KEY tem de ter pelo menos 32 caracteres. "
                'Gera um com: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        return value

    @model_validator(mode="after")
    def _secret_key_not_placeholder_in_production(self) -> "Settings":
        lowered = self.secret_key.lower()
        if self.is_production and any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
            raise ValueError(
                f"SECRET_KEY parece ser um valor por omissão ({self.secret_key!r}) — "
                "define um segredo real fora do ambiente de desenvolvimento."
            )
        return self


settings = Settings()
