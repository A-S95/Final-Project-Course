# CentiSible

Plataforma de gestão de finanças pessoais — projeto final de curso, full-stack (Python/FastAPI + React/TypeScript + PostgreSQL).

## Funcionalidades

- **Landing page** pública com apresentação do produto, antes do login/registo.
- **Autenticação**: registo/login com JWT (access token em memória + refresh token rotativo em cookie `httpOnly`, com deteção de reutilização).
- **Contas**: multi-conta (banco, carteira, poupança, cartão de crédito, outra), com saldo atualizado a cada transação.
- **Categorias**: separadas por tipo (receita/despesa), usadas em transações, orçamentos e despesas recorrentes.
- **Transações**: receitas, despesas e transferências entre contas próprias, com filtros por conta/categoria/tipo/data; despesas podem ser marcadas como "partilhadas" com o agregado.
- **Dashboard**: resumo do mês (saldo, receitas, despesas, poupança), despesas por categoria em gráfico, alertas automáticos ("insights").
- **Orçamentos mensais** por categoria, com barra de progresso e aviso ao aproximar/ultrapassar o limite.
- **Despesas recorrentes**: geração automática de transações recorrentes (renda, subscrições, ...).
- **Objetivos financeiros**: metas de poupança com prazo e contribuições registadas ao longo do tempo.
- **Histórico e analytics**: comparação com o mês anterior e evolução dos últimos 6 meses.
- **Agregado familiar**: partilha de despesas entre membros de um agregado, com convites, vista de dashboard combinada e despesas partilhadas contadas uma só vez (não duplicadas por categoria).
- **Definições**: nome, moeda e rendimento mensal editáveis.
- **Tema claro/escuro**: segue o sistema por omissão, com alternador manual persistido.

Documentação completa em [`docs/`](docs/):
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitetura, requisitos, modelo de dados, ERD, roadmap, decisões técnicas.
- [`docs/DEV_JOURNAL.md`](docs/DEV_JOURNAL.md) — diário de desenvolvimento: decisões tomadas, alternativas consideradas, problemas e soluções (apoio à apresentação/defesa).

## Stack

**Backend**: Python, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Pydantic
**Frontend**: React, TypeScript, Vite, React Router, TanStack Query, React Hook Form + Zod, Tailwind CSS, shadcn/ui, Framer Motion, Recharts
**Infra**: Docker, Docker Compose, GitHub Actions

## Estrutura

```
backend/     # API FastAPI (Dockerfile de dev + Dockerfile.prod)
frontend/    # SPA React (Dockerfile de dev + Dockerfile.prod, e2e/ com testes Playwright)
docs/        # documentação do projeto
docker-compose.yml        # stack de desenvolvimento
docker-compose.prod.yml   # stack de produção (ver secção "Deployment")
```

## Como correr

### Com Docker (recomendado)

Requer [Docker](https://www.docker.com/products/docker-desktop/) instalado.

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up
```

O `SECRET_KEY` do `.env.example` só serve para desenvolvimento — para qualquer
deployment real, gera um com `python -c "import secrets; print(secrets.token_hex(32))"`
(a app recusa-se a arrancar com o valor por omissão quando `ENVIRONMENT != development`).

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (docs interativas em `/docs`)
- PostgreSQL: `localhost:5432` (user/pass/db: `fintrack`)

### Sem Docker (backend)

Requer Python 3.12+ e [uv](https://docs.astral.sh/uv/).

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

### Sem Docker (frontend)

Requer Node.js 22+.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Testes

```bash
# backend
cd backend && uv run pytest

# frontend
cd frontend && npm run lint

# E2E (Playwright) — precisa da app a correr (docker compose up, ou dev manual)
cd frontend && npx playwright install chromium --with-deps   # só na primeira vez
cd frontend && npm run test:e2e
```

## Deployment (produção)

`docker-compose.prod.yml` sobe uma versão de produção da stack: frontend
compilado como estático e servido por nginx (em vez do servidor Vite de
desenvolvimento), backend a correr `uvicorn` sem `--reload` e sem `uv` na
imagem final, e o Postgres sem a porta exposta ao host.

```bash
cp .env.prod.example .env.prod
# editar .env.prod: POSTGRES_PASSWORD, SECRET_KEY, CORS_ORIGINS, VITE_API_URL

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

- Frontend (nginx): http://localhost (porta 80)
- Backend: http://localhost:8000

Notas importantes:
- `SECRET_KEY` tem de ser gerado com `python -c "import secrets; print(secrets.token_hex(32))"` — a app recusa-se a arrancar em produção com um valor que pareça um placeholder esquecido.
- `VITE_API_URL` é embebido no bundle do frontend **em tempo de build** (é como o Vite funciona — não é lido em runtime pelo browser). Se a API tiver um domínio público diferente de `http://localhost:8000`, é preciso reconstruir a imagem do frontend depois de mudar esta variável.
- As migrações da base de dados (`alembic upgrade head`) correm automaticamente no arranque do container do backend, antes do servidor aceitar pedidos.
- Este setup não inclui TLS/HTTPS nem um domínio público — isso fica a cargo da infraestrutura onde for feito o deploy (ex: um reverse proxy como Caddy/nginx-proxy à frente desta stack, ou um serviço gerido que já trate disso), propositadamente fora do âmbito deste projeto.
