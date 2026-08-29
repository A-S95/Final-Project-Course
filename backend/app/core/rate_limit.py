from slowapi import Limiter
from slowapi.util import get_remote_address

# Guardado em memória do processo (sem Redis) — suficiente para a escala desta
# app (um único utilizador típico, sem múltiplas instâncias atrás de um load
# balancer). Em produção com `UVICORN_WORKERS > 1` (ver Dockerfile.prod), cada
# worker tem a sua própria contagem — o limite efetivo multiplica-se pelo
# número de workers. Aceitável aqui; um backend partilhado (Redis) resolveria
# isto se a app crescesse para múltiplas instâncias.
#
# `enabled` começa a `True` e é desligado explicitamente nos testes (ver
# `tests/conftest.py`) para não fazer a suite de testes tropeçar no limite —
# os testes dedicados de rate limiting voltam a ligá-lo antes de cada teste.
limiter = Limiter(key_func=get_remote_address, enabled=True)
