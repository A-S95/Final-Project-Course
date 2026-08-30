# CentiSible

Gestão de finanças pessoais e familiares — projeto final de curso, full-stack (Python/FastAPI + React/TypeScript + PostgreSQL).

## Demo ao vivo

**[centisible.vercel.app](https://centisible.vercel.app)**

Contas de teste prontas a usar: `teste1@teste.com` a `teste10@teste.com`, password `Teste1234` (cada uma com ~2 anos de dados). Também instalável como app no telemóvel (PWA) direto do browser.

> O backend corre num plano gratuito que adormece ao fim de 15 min sem pedidos — o primeiro acesso depois de uma pausa pode demorar 30-60s a responder.

## Funcionalidades

- Contas (banco, carteira, poupança, cartão), com saldo atualizado a cada movimento, e validade/plafond para cartões
- Categorias, transações (receita/despesa/transferência) e recibos anexados a uma transação
- Orçamentos mensais por categoria, objetivos de poupança com prazo, despesas recorrentes
- Dashboard com resumo do mês, gráfico por categoria e alertas automáticos ("insights")
- Histórico e comparação mês a mês
- Agregado familiar: convites, dashboard combinado, despesas partilhadas contadas uma só vez
- Autenticação com JWT + refresh token rotativo, tema claro/escuro, instalável como PWA

Documentação completa em [`docs/`](docs/):
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitetura, modelo de dados, ERD, decisões técnicas.
- [`docs/DEV_JOURNAL.md`](docs/DEV_JOURNAL.md) — diário de desenvolvimento: decisões, problemas e soluções.

## Stack

**Backend**: Python, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Pydantic
**Frontend**: React, TypeScript, Vite, TanStack Query, React Hook Form + Zod, Tailwind CSS, Framer Motion, Recharts, `vite-plugin-pwa`
**Infra**: Docker Compose (dev), GitHub Actions (CI), Vercel + Render + Neon (produção)

## Como correr localmente

Requer [Docker](https://www.docker.com/products/docker-desktop/).

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (`/docs` para o Swagger)
- PostgreSQL: `localhost:5432` (user/pass/db: `fintrack`)

<details>
<summary>Sem Docker</summary>

**Backend** (Python 3.12+, [uv](https://docs.astral.sh/uv/)):
```bash
cd backend && cp .env.example .env && uv sync
uv run uvicorn app.main:app --reload
```

**Frontend** (Node.js 22+):
```bash
cd frontend && cp .env.example .env && npm install
npm run dev
```
</details>

## Testes

```bash
cd backend && uv run pytest              # testes de backend
cd frontend && npm run lint              # lint do frontend

cd frontend && npx playwright install chromium --with-deps   # só na primeira vez
cd frontend && npm run test:e2e          # E2E — precisa da app a correr
```

## Deployment

Em produção: frontend na **Vercel**, backend na **Render** (a partir do `backend/Dockerfile.prod`), base de dados na **Neon**. Porquê esta combinação em vez de um único `docker-compose.prod.yml` num servidor: ver `docs/ARCHITECTURE.md` (secção "Hospedagem em produção") e `docs/DEV_JOURNAL.md`.

Para auto-hospedar com Docker Compose em vez disso:

```bash
cp .env.prod.example .env.prod
# editar: POSTGRES_PASSWORD, SECRET_KEY, CORS_ORIGINS, VITE_API_URL

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Notas:
- `SECRET_KEY` tem de ser gerado com `python -c "import secrets; print(secrets.token_hex(32))"` — a app recusa-se a arrancar em produção com um valor que pareça um placeholder esquecido.
- `VITE_API_URL` é embebido no bundle **em tempo de build**, não é lido em runtime. Mudar o domínio da API exige reconstruir a imagem do frontend.
- As migrações (`alembic upgrade head`) correm automaticamente no arranque do backend.
- Este setup não inclui TLS/domínio próprio — fica a cargo de onde for feito o deploy.
