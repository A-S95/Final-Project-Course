from slowapi import Limiter
from slowapi.util import get_remote_address

# Em memória do processo (sem Redis) — com UVICORN_WORKERS > 1 cada worker conta à
# parte, o limite efetivo multiplica-se. Aceitável a esta escala; Redis resolveria.
# `enabled` é desligado nos testes (`tests/conftest.py`) exceto nos dedicados a isto.
limiter = Limiter(key_func=get_remote_address, enabled=True)
