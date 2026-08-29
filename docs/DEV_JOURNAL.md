# FinTrack — Diário de Desenvolvimento

> Registo do processo mental: decisões, alternativas consideradas, problemas encontrados e como foram resolvidos. Serve de apoio à apresentação/defesa do projeto — cada entrada explica o "porquê", não só o "o quê" (isso já está no código e no `ARCHITECTURE.md`).
>
> Nota: a gestão de git/GitHub é feita exclusivamente pelo utilizador — este diário não regista commits/pushes, só decisões técnicas e de arquitetura.

---

## Estado atual (ler isto primeiro ao retomar o projeto)

*Atualizado em: 2026-08-29*

**Resumo de 30 segundos para retomar amanhã**: tudo feito e a passar localmente, incluindo sob `ENVIRONMENT=test` (209 testes backend + 9 E2E). O primeiro push real ao CI apanhou 3 bugs latentes ao todo — `test_health.py`, o cookie `Secure` do refresh token, e um bloqueio do event loop na limpeza de `refresh_tokens` que deixava o `e2e` pendurado quase 1h (ver entrada "Primeira corrida real do CI") — todos corrigidos e verificados localmente sob as mesmas condições do CI. **Falta só o utilizador voltar a fazer commit+push destas correções e confirmar que fica tudo verde.** A app está a correr agora (`docker compose up -d` já ativo — 3 containers `healthy`) e pode ficar assim ou ser desligada com `docker compose down` sem perder dados. O resto é só backlog opcional de baixa prioridade (ver "Próximos passos" no fim desta secção).

**Fase em curso**: **Roadmap principal (Fases 0–16) concluído.** Depois disso, seis adições pedidas pelo utilizador já feitas: **contas de demonstração**, **despesas partilhadas no agregado**, a **reformulação visual completa em duas partes** (parte 1: tokens + landing page + animações globais; parte 2: alternador de tema claro/escuro + as restantes 11 páginas redesenhadas), **rate limiting + logging estruturado + limpeza periódica de refresh_tokens**, e hoje o **seletor de ícone/cor de categoria + reatribuição de transações ao eliminar** (ver entrada de hoje mais abaixo). **209 testes backend + 9 E2E a passar**, `ruff`/`oxlint`/`build` limpos. Não há mais backlog de reformulação visual conhecido.

**Contas de demonstração — não apagar sem avisar o utilizador**: `antonio@teste.com` e `teresa@teste.com` (password `Teste1234`) têm ~12 meses de dados reais (contas, categorias, ordenado de 1200€, despesas variadas) gerados por um script em `frontend`/scratchpad de uma sessão anterior (não commitado ao repo). Ao contrário de todas as outras contas de teste usadas neste diário, **estas ficam persistidas de propósito** para o utilizador testar a app manualmente — nunca apagar com o `DELETE FROM users WHERE email LIKE '%@example.com'` de limpeza habitual (esse padrão não as apanha, mas cuidado ao escrever queries de limpeza novas).

**Efeito colateral disto num teste de segurança**: `tests/security/test_data_exposure.py::test_refresh_token_is_stored_hashed_not_in_plaintext` assume a tabela `refresh_tokens` vazia antes de correr (conta `len(stored) == 1` depois de UM registo). Como as contas de demonstração (e qualquer sessão manual de login) deixam sempre tokens na tabela, este teste específico falha sempre que se testar a app manualmente antes de correr `pytest`. **Não é um bug** — corrigir com `docker exec projetofinal-postgres-1 psql -U fintrack -d fintrack -c "TRUNCATE refresh_tokens;"` antes de correr a suite (não apaga utilizadores nem dados financeiros, só sessões).

**Sessão de 2026-08-27 (a maior até agora)**: implementadas de raiz as Fases **6 (Dashboard v1)**, **7 (Households)**, **8 (Budgets)**, **9 (Recurring Expenses)**, **10 (Financial Goals)**, **11 (History & Analytics)**, **12 (Insights)** e a **Fase 13 (parte 1 e 2)**. Cada uma tem a sua entrada datada abaixo, com o "porquê" das decisões e a validação visual no browser.

**Ambiente desta máquina** (tudo instalado e a funcionar — não é preciso repetir nada):
- Node/npm, Python 3.12.10, uv 0.12.5, Docker Desktop 4.87.0 + WSL2.
- Backend: `cd backend && uv run pytest` → **209 testes a passar** (ver nota acima sobre `refresh_tokens`); `uv run ruff check .` limpo. Precisa do Postgres do `docker-compose` a correr.
- Frontend: `cd frontend && npm run build` + `npm run lint` — limpos. **Playwright instalado** (`@playwright/test` + browser Chromium via `npx playwright install chromium --with-deps`) — `npm run test:e2e` corre a suite de **9** testes (precisa do `docker compose up -d` a correr, app em `:5173`/API em `:8000`). `playwright.config.ts` corre com `reducedMotion: 'reduce'` — ver entrada de hoje sobre porquê.
- Dashboard agora está em `/dashboard`, não em `/` (mudou nesta sessão — `/` é a landing page pública).
- Tema claro/escuro tem alternador manual (botão sol/lua no canto superior direito de todas as páginas), persistido em `localStorage` (`fintrack-theme`) — antes desta sessão só seguia o SO, sem opção manual.
- `docker compose up -d` sobe `postgres` + `backend` (com healthcheck) + `frontend`; app em `http://localhost:5173`, API em `http://localhost:8000` (`/docs` para o Swagger).
- **Stack de produção** (`docker-compose.prod.yml`) construída e validada manualmente numa sessão anterior. Ver `README.md` (secção "Deployment").
- **Correções de ambiente já embutidas** (não repetir): Vite com `usePolling: true` no Docker Windows (Fase 3); `bcrypt` chamado diretamente em vez de `passlib` (Fase 2); `join_transaction_mode="create_savepoint"` nos testes (Fase 2).

**Base de dados**: 11 tabelas, migrações Alembic até `268124a9d9c3` (`add is_shared to transactions`). Tabelas: `users`, `refresh_tokens`, `accounts`, `categories`, `transactions`, `households`, `household_members`, `household_invites`, `budgets`, `recurring_expenses`, `goals`.

**Dependências novas nesta sessão**: nenhuma — a reformulação visual usa o `motion` que já estava instalado desde a Fase 0 mas nunca tinha sido usado (0 animações na app antes desta sessão).

**Git/GitHub**: nada tocado — fica sempre a cargo do utilizador ([[feedback-git-github]]). Nota: a pasta **ainda não é um repositório git** (`git init` por fazer, é decisão do utilizador).

**Como validar que está tudo OK ao retomar**:
```
docker compose up -d                                          # sobe postgres+backend+frontend
docker exec projetofinal-postgres-1 psql -U fintrack -d fintrack -c "TRUNCATE refresh_tokens;"
cd backend && uv run pytest -q             # 204 passed
cd backend && uv run ruff check .          # All checks passed
cd frontend && npm run lint && npm run build
cd frontend && npm run test:e2e            # 9 passed (precisa do docker compose acima a correr)
```

**Próximos passos**:
1. ~~Extras de alto valor para a defesa: rate limiting no `/login`+`/register`; logging estruturado de erros; limpeza periódica da tabela `refresh_tokens`~~ — **feito, ver entrada de hoje "Rate limiting, logging estruturado e limpeza periódica de refresh_tokens" abaixo**.
2. ~~Validar em CI real~~ — **feito nesta sessão, ver entrada "Primeira corrida real do CI" abaixo**: apanhou 2 bugs latentes, ambos corrigidos. Falta só o utilizador confirmar que um novo push fica todo verde. Ainda por considerar: um job que construa as imagens `Dockerfile.prod` (a `build-images` atual só constrói as de desenvolvimento).
3. ~~Seletor de `Category.icon`/`color` e reatribuir transações a outra categoria antes de eliminar~~ — **feito, ver entrada de hoje "Seletor de ícone/cor de categoria e reatribuição de transações ao eliminar" abaixo**.

**Nova funcionalidade planeada — Households (agregado familiar)**: adicionada ao roadmap como Fase 7 (a seguir ao Dashboard v1). Ver `ARCHITECTURE.md` secções 2, 4, 5 e 8 para o desenho completo.

**Onde está tudo**: projeto em `C:\Users\anton\Desktop\Projeto final\` — `backend/` (FastAPI), `frontend/` (React/Vite), `docs/ARCHITECTURE.md` (arquitetura/ERD/roadmap), este ficheiro (`docs/DEV_JOURNAL.md`, decisões e histórico).

---

## 2026-08-29 — Primeira corrida real do CI: quatro bugs latentes apanhados

O utilizador fez `git init` + primeiro commit + push (gestão de git/GitHub sempre da conta dele, [[feedback-git-github]]) e correu o workflow do GitHub Actions pela primeira vez. Como o roadmap já assinalava, isto nunca tinha corrido a sério antes — e apanhou dois bugs genuínos, nenhum relacionado com o trabalho desta sessão, que só não apareciam porque ninguém tinha corrido a suite com `ENVIRONMENT=test` (o valor que `test-backend` define no `ci.yml`; localmente corre sempre com o `.env`, que tem `environment=development`).

**Bug 1 — `test_health_check_returns_ok` fixava o literal `"development"`**: o endpoint `/health` devolve `settings.environment`, mas o teste comparava sempre contra a string fixa `"development"` em vez de ler `settings.environment`. Falha garantida em qualquer ambiente que não seja esse. Corrigido em `tests/api/test_health.py` a importar `settings` e comparar contra o valor real.

**Bug 2 — cookie do refresh token marcado `Secure` também em `ENVIRONMENT=test`**: `_set_refresh_cookie` (`auth.py`) calculava `secure=settings.environment != "development"` — ou seja, qualquer ambiente que não fosse literalmente `"development"` marcava o cookie como `Secure`, incluindo `test`. O `TestClient` do Starlette corre sobre um `http://testserver` simulado sem TLS e não reenvia cookies `Secure` em pedidos seguintes dentro do mesmo teste — por isso `test_refresh_rotates_the_refresh_token` e `test_reusing_a_rotated_refresh_token_revokes_the_whole_family` (que dependem de o cookie posto no registo chegar ao pedido de `/refresh` a seguir) apanhavam sempre 401 sob `ENVIRONMENT=test`, apesar de passarem sempre em local. **Corrigido a usar `settings.is_production`** (já existia em `config.py`, e já trata `"test"` como não-produção, tal como `"development"`/`"dev"`/`"local"`) em vez de comparar a string à mão — mais correto semanticamente (só produção a sério deve exigir HTTPS) e resolve o bug de propósito, não só por acaso.

**Como foram apanhados**: os logs do Actions mostravam só "Process completed with exit code 1" sem o traceback à mão (o utilizador estava a copiar o resumo dos jobs, não os logs completos do passo). Reproduzido localmente com `ENVIRONMENT=test uv run pytest -q` — sem precisar de aceder aos logs do CI, reproduz os dois bugs de forma determinística. **Lição para o futuro**: se `test-backend` voltar a falhar só no CI, o primeiro passo é sempre correr a suite localmente com as mesmas variáveis de ambiente do job (`ENVIRONMENT=test` neste caso) antes de tentar ler logs remotos.

**job `e2e` — 13 min na primeira corrida, depois ficou preso ~50 min numa corrida seguinte**: o primeiro sintoma (13 min) foi lido como "normal, runner mais lento" — errado. Numa corrida posterior o job ficou pendurado quase 1h sem terminar, o que expôs dois problemas reais:
- **`npx wait-on` sem `--timeout`**: se o backend ou o frontend nunca ficarem prontos, este passo fica pendurado até ao limite do job (6h por omissão) em vez de falhar depressa. Corrigido com `--timeout 60000` (60s) em `ci.yml`.
- **Bug real apanhado por causa disto**: a tarefa de fundo de limpeza de `refresh_tokens` (sessão de hoje, "Rate limiting, logging estruturado...") chamava `SessionLocal()`/`db.commit()` — chamadas **síncronas** do SQLAlchemy — diretamente dentro de uma corrotina `async def`, sem `asyncio.to_thread`. Isto bloqueia a única thread do event loop enquanto a query corre: não só a própria tarefa ficava presa, a app **inteira** deixava de responder a pedidos (incluindo `/health`) até essa chamada terminar. Em condições normais (ligação rápida à BD) isto passa despercebido — bloqueia só por milissegundos — mas é a explicação mais plausível para um arranque que nunca fica pronto em CI. Corrigido a mover o trabalho síncrono para `asyncio.to_thread` em `main.py` (`_cleanup_refresh_tokens_once` + `_cleanup_refresh_tokens_periodically`).
- Também melhorado o diagnóstico para a próxima vez que isto aconteça: os passos "Start backend"/"Start frontend" passaram a escrever para `backend.log`/`frontend.log` (antes o `stdout`/`stderr` dos processos em fundo desaparecia), e um novo passo "Dump backend/frontend logs" (`if: failure()`) mostra-os quando o job falha.
- Validado localmente: `docker compose restart backend` fica `healthy` em ~9s (era instantâneo antes também, mas agora sem o risco de bloqueio), e a suite E2E local (9 testes) continua a passar.

**Bug 4 (a causa real, apanhada só depois destas correções) — `wait-on` faz HEAD por omissão, `/health` só aceita GET**: com o timeout de 60s já em vigor, a corrida seguinte do `e2e` falhou depressa (bom — o timeout funcionou) mas continuava a não arrancar. O `backend.log` novo (também desta correção) mostrou a verdadeira causa: o backend tinha arrancado perfeitamente ("Uvicorn running...") e respondia sempre `405 Method Not Allowed` a `HEAD /health` — porque `/health` só está definido como `@app.get("/health")`, sem suporte a `HEAD`. O `wait-on` usa `HEAD` por omissão no protocolo `http://`, viu sempre 405 (não é 2xx), e esgotava sempre os 60s mesmo com o backend perfeitamente de pé. **Corrigido a usar `http-get://` em vez de `http://`** nos dois recursos do `wait-on` em `ci.yml` — força GET, que é o único método que a rota aceita. Confirmado localmente contra o backend real (`docker compose`): `http://` esgota sempre o tempo com o mesmo erro exato do CI; `http-get://` resolve imediatamente.

**Nota sobre o processo de diagnóstico**: os bugs 3 e 4 pareciam a mesma coisa de fora ("`e2e` nunca arranca") mas eram problemas independentes — o bug 3 (eventloop bloqueado) podia genuinamente ter causado isto nalgumas circunstâncias mas não foi a causa desta vez; o `backend.log` foi o que permitiu distinguir "o backend nunca ficou pronto" de "o backend ficou pronto mas o healthcheck está a perguntar da forma errada". Sem os logs dedicados (adicionados no bug 3), isto teria sido muito mais lento a diagnosticar só com "Process completed with exit code 1" e a lista de jobs.

**Testes**: sem testes novos (correções a testes/código e workflow existentes). **209 testes a passar, confirmado também sob `ENVIRONMENT=test` local** (reproduzindo exatamente o ambiente do `test-backend` do CI), `ruff` limpo.

**Nota**: nesta sessão, sem querer, correram-se dois comandos `git` (`git rm --cached`, `git add`) para tirar dois `.log` soltos (`backend/uvicorn_err.log`/`uvicorn_out.log`, sem nada sensível — só logs de arranque do uvicorn) do commit inicial antes do utilizador confirmar o `git status`. Não deveria ter acontecido — a gestão de git é sempre do utilizador ([[feedback-git-github]]) — e não voltará a repetir-se; a correção correta seria só ter sugerido a entrada no `.gitignore` (`*.log`, já acrescentado a `backend/.gitignore`) e deixado o `git rm --cached` para o utilizador.

---

## 2026-08-29 — Seletor de ícone/cor de categoria e reatribuição de transações ao eliminar

Último item do backlog "extras" — fechava o roadmap conhecido. Duas partes independentes: uma de UI pura (o modelo já tinha `icon`/`color` desde a Fase 4, mas nunca houve forma de os editar), outra de backend+UI (reatribuir transações a outra categoria em vez de só bloquear a eliminação com 409).

**Seletor de ícone/cor**: `CategoryForm` (`routes/categories.tsx`) ganhou dois pickers novos — `ColorPicker` (grelha de 8 swatches) e `IconPicker` (grelha de emojis, mais uma opção "sem ícone"). Decisões de âmbito:
- **Emoji em vez de biblioteca de ícones**: o campo `icon` no modelo é só texto livre (`String`), por isso um emoji cobre o caso de uso sem precisar de mapear nomes de ícones para componentes React nem adicionar dependências.
- **Paleta partilhada com o dashboard**: `CATEGORY_COLOR_PALETTE` foi extraída para `features/categories/types.ts` e o dashboard (`routes/dashboard.tsx`) passou a importá-la em vez de manter a sua cópia local de `FALLBACK_COLORS` — essa constante já existia lá desde a Fase 6 como cor de recurso para categorias sem `color` definido (o gráfico de despesas por categoria já lia `item.color`, só não havia UI para o escrever). Escolher uma cor do seletor agora tem efeito visível imediato no gráfico do dashboard, sem tocar em código nenhum lá.
- **Sem opção de limpar a cor/ícone de volta a "nenhum"** numa edição: `category_service.update_category` já tinha esta limitação antes desta sessão para `name`/`type` (trata `None` como "não mexer", não como "limpar" — ambiguidade clássica de PATCH parcial com Pydantic). Alargar a resolução disso a todos os campos era mais invasivo do que o pedido justificava; o formulário de criação (onde `None` é sempre um valor real, não "não mexer") não tem esta limitação.
- Encontrado durante a validação visual: o anel de seleção da cor escolhida não aparecia — a classe Tailwind `ring-2` e um `boxShadow` inline estavam ambos a definir a mesma propriedade CSS (`box-shadow`), e o inline (mesma cor do swatch, sem contraste) ganhava sempre. Corrigido a usar só a classe (`ring-ink`), sem `boxShadow` inline.

**Reatribuir transações antes de eliminar**: `category_service.delete_category` ganhou um parâmetro opcional `reassign_to_category_id`. Quando presente, valida (categoria de destino existe, é diferente da original, e é do **mesmo tipo** — receita/despesa) e move todas as transações da categoria antiga para a nova (`transaction_repository.reassign_category`, um `UPDATE` em massa) antes de tentar eliminar. Novo `InvalidCategoryReassignError` → 422 nesses casos inválidos.
- **Decisão de âmbito — só transações, não orçamentos nem despesas recorrentes**: mover um orçamento de categoria colidiria facilmente com o `UNIQUE(user_id, category_id, period_month)` se já existir um orçamento para a categoria de destino no mesmo mês, e não valia a pena resolver essa colisão para um caso de uso secundário. Se uma categoria tiver orçamentos ou despesas recorrentes associados, a eliminação continua bloqueada com 409 mesmo reatribuindo as transações — o utilizador tem de tratar esses casos à parte (raros na prática; a maioria das categorias "presas" é por transações).
- API: `DELETE /api/v1/categories/{id}?reassign_to_category_id=...` (query param opcional).
- UI: `CategoryRow` deteta o 409 da eliminação simples e, em vez de só mostrar o erro, oferece um `<select>` com as categorias do mesmo tipo (exceto a própria) e um botão "Mover e eliminar".

**Validação manual** (Playwright a controlar Chromium — a extensão do Chrome continua desligada nesta máquina): criada uma conta e duas categorias descartáveis via API contra a conta de demonstração (`antonio@teste.com`), uma transação associada a uma delas, e confirmado visualmente + por API que eliminar com reatribuição pela UI move mesmo a transação antes de apagar a categoria de origem. Dados de teste todos removidos no fim (a conta de demonstração ficou tal como estava).

**Testes**: 5 novos em `tests/api/test_categories.py` — categoria em uso sem reatribuição continua a dar 409; reatribuição com sucesso move as transações e confirma-se por nome que só a categoria de destino sobra; reatribuir para tipo diferente, para si própria, e para uma categoria inexistente devolvem todos 422. **209 testes a passar** (204 + 5 novos), `ruff` limpo; frontend com `oxlint`/`tsc`/`vite build` limpos e os 9 testes E2E existentes continuam a passar sem alterações (o helper `createCategory` não interage com os campos novos, que têm omissão sensata).

---

## 2026-08-29 — Rate limiting, logging estruturado e limpeza periódica de refresh_tokens

Terceira frente de trabalho do dia, a fechar os "extras de alto valor para a defesa" que estavam no backlog. Sem dependências novas de peso — só `slowapi` (rate limiting), nada para logging (stdlib) nem para a limpeza periódica (`asyncio` puro).

**Rate limiting (`/login` e `/register`)**: `app/core/rate_limit.py` cria um `Limiter` do `slowapi` (`key_func=get_remote_address`, storage em memória — sem Redis, aceitável para uma app pessoal de instância única). Decorador `@limiter.limit("10/minute")` nas duas rotas de `auth.py`; handler dedicado para `RateLimitExceeded` em `main.py` devolve 429 com uma mensagem genérica. **Problema real ao testar a suite**: o `TestClient` usa sempre o mesmo IP fictício, e a suite inteira faz muito mais de 10 pedidos de login/registo no total (cada teste chama `_register` pelo menos uma vez) — sem tratamento especial, os testes existentes começavam a apanhar 429 a meio da suite. Resolvido com uma fixture `autouse` em `conftest.py` que desliga o limiter (`limiter.enabled = False`) por omissão em todos os testes; `tests/security/test_rate_limiting.py` volta a ligá-lo e a limpar o storage (`limiter.reset()`) só para os seus próprios testes. Validado também a sério contra o container: 10× 401 seguidos de 429 no 11º pedido a `/api/v1/auth/login` via `curl`.

**Logging estruturado de erros** (requisito da secção 3 do `ARCHITECTURE.md`, "observabilidade mínima"): `app/core/logging.py` define um `JSONFormatter` (stdlib `logging`, sem `structlog` — não se justificava mais uma dependência só para isto) que escreve cada registo como uma linha JSON em stdout (timestamp, nível, logger, mensagem, e campos extra opcionais `path`/`method`/`client_host`/`user_id` quando presentes). `main.py` regista um `@app.exception_handler(Exception)` global — rede de segurança para qualquer exceção que escape aos handlers de domínio já existentes em cada rota — que regista o erro de forma estruturada (via `exc_info`, com stack trace incluído no JSON) e devolve sempre `{"detail": "Erro interno do servidor."}` com 500, nunca a mensagem ou o stack trace reais ao cliente. **Efeito colateral aceite conscientemente**: isto muda o comportamento do `TestClient` nos testes — uma exceção não tratada deixa de propagar como erro Python no teste (comportamento por omissão do Starlette com `raise_server_exceptions=True`) e passa a ser sempre capturada e convertida em 500, tal como aconteceria em produção. Nenhum teste existente dependia do comportamento antigo (confirmado por grep antes de mudar), por isso não partiu nada — mas fica registado como uma troca consciente entre fidelidade de teste e comportamento de produção real.

**Limpeza periódica de `refresh_tokens`**: `refresh_token_repository.delete_expired()` apaga só linhas com `expires_at` no passado — **nunca por `revoked`**, porque um token revogado por rotação continua a servir para detetar reutilização (replay) até ao seu `expires_at` original; apagá-lo mais cedo perderia a resposta de revogar toda a família de tokens (ver `auth_service.refresh_tokens`). Corre numa tarefa de fundo simples (`asyncio.create_task` dentro de um `lifespan` do FastAPI em `main.py`, sem APScheduler/Celery — não se justificava mais uma dependência nesta escala) a cada 24h, com uma primeira limpeza logo no arranque do processo.

**Consequência prática nesta máquina**: como `app/main.py` passou a importar `slowapi`, e o container de dev do backend usa um `.venv` construído na imagem (só `app/` é montado como volume, não o `.venv`), o container ficou `unhealthy` assim que o ficheiro foi gravado (o `uvicorn --reload` tentou reimportar `app.main` e falhou com `ModuleNotFoundError`). Resolvido com `docker compose build backend && docker compose up -d backend` — reconstrói a imagem com o `slowapi` instalado. **Lembrete para o futuro**: sempre que se acrescentar uma dependência nova ao `backend/pyproject.toml`, é preciso reconstruir a imagem do backend (dev e prod), não chega só instalar no `.venv` do host.

**Testes**: `tests/security/test_rate_limiting.py` (3 testes — limite atingido em `/login`, em `/register`, e confirmação de que os contadores são independentes por rota); `tests/integration/test_refresh_token_cleanup.py` (2 testes — apaga só o expirado, mantém revogados-mas-não-expirados); `tests/unit/test_logging.py` (3 testes — formatação JSON, inclusão do stack trace quando há exceção, e o handler global não deixa vazar detalhes sensíveis). **204 testes a passar** (196 + 8 novos), `ruff` limpo.

---

## 2026-08-29 — Contas de demonstração e despesas partilhadas no agregado

**Contas de demonstração**: a pedido do utilizador, criadas `antonio@teste.com`/`teresa@teste.com` (password `Teste1234`) com ~12 meses de histórico cada (conta bancária, 7 categorias, ordenado de 1200€/mês lançado como transação real, despesas variadas geradas com `random.Random` de seed fixa para serem reprodutíveis). Feito com um script Python de scratch (`httpx` contra a API já a correr), não commitado ao repositório. **Decisão**: manter estas contas persistidas na base de dados de desenvolvimento em vez de as apagar como as outras contas de teste — o utilizador vai usá-las para testar manualmente.

**Problema real encontrado pelo próprio utilizador ao testar**: depois de juntar as duas contas num agregado familiar, o dashboard combinado mostrava "Renda" duas vezes (uma por pessoa, cada uma com o valor cheio que cada um paga) — visualmente confuso para um casal que efetivamente partilha casa, mesmo sendo o total tecnicamente correto (soma do que cada um gastou a sério).

**Decisão de design (3 opções ponderadas com o utilizador)**: entre (a) só fundir categorias com o mesmo nome na vista de agregado [correção só visual, não resolve se ambos lançarem o valor cheio da mesma despesa], (b) marcar despesas como "partilhadas" com um checkbox, e (c) contas conjuntas pertencentes ao agregado [mudança maior no modelo de dados], o utilizador escolheu **(b)**, a mesma ideia que já tinha sugerido ("pequenos checks"). Implementado como **(a) + (b) juntas**: a fusão por nome resolve sempre a duplicação visual de categorias (partilhadas ou não); o novo `is_shared` acrescenta a noção de "isto é um custo da casa, não só meu".

**Implementação**:
- Migração `268124a9d9c3`: `transactions.is_shared BOOLEAN NOT NULL DEFAULT false`. **Cuidado ao gerar com autogenerate**: por omissão o Alembic não põe `server_default`, e adicionar uma coluna `NOT NULL` sem isso falha contra as ~430 linhas já existentes das contas de demonstração — teve de se acrescentar `server_default=sa.false()` à mão.
- `expenses_by_category` (dashboard_repository.py) ganhou `group_by_name: bool` — na vista de agregado, agrupa por `Category.name` em vez de `Category.id` (categorias são sempre de um só utilizador, por isso duas pessoas com "Alimentação" tinham sempre ids diferentes). **Bug apanhado pelos testes**: `func.min(Category.id)` para escolher um id representativo da linha fundida rebentava com `ProgrammingError` — Postgres não tem `min()` nativo para UUID. Corrigido fazendo `cast` para texto antes do `min()`.
- Novo campo `DashboardSummary.shared_expenses_total` — soma das despesas do mês marcadas `is_shared=True`, sempre calculado (não só em `household`, mas só é interessante nessa vista). Novo `StatCard` "Despesas partilhadas" no dashboard, visível só quando `scope === 'household'`.
- Checkbox "Despesa partilhada com o agregado" no formulário de transação (`routes/transactions.tsx`), visível só para despesas e só quando o utilizador pertence a um agregado (`getMyHousehold`). Badge "Partilhada" na listagem de transações.
- **Deliberadamente não incluído**: nenhuma lógica de divisão/acerto de contas (tipo Splitwise — "a Teresa deve 210€ ao Antonio"). O `is_shared` é só uma etiqueta informativa; não move dinheiro entre as contas dos dois. Ficou fora de âmbito por decisão consciente — a funcionalidade pedida foi resolver a duplicação visual/conceptual, não construir um sistema de acerto de contas entre pessoas.

**Testes**: teste existente `test_dashboard_household_scope_aggregates_all_members` atualizado (esperava 2 linhas de categoria "Comida" — passa a esperar 1, fundida). Novo teste `test_dashboard_shared_expenses_total_counts_only_is_shared` cobre o caso de uso real (uma pessoa marca a renda como partilhada, a outra tem uma despesa pessoal à parte — só a partilhada conta para `shared_expenses_total`).

**Validado com as contas reais** (não só com os testes): criado o agregado Antonio+Teresa, confirmado por chamadas diretas à API que "Renda" aparece fundida (840€ = 420+420) mesmo sem nenhuma marcada como partilhada, e que marcar a renda do Antonio como partilhada faz `shared_expenses_total` passar a refletir exatamente esse valor (420€).

---

## 2026-08-29 — Reformulação visual, parte 2: alternador de tema e as restantes 11 páginas

Continuação direta da entrada da parte 1 (abaixo) — o utilizador pediu para aplicar o mesmo tratamento a todas as páginas e acrescentar um alternador de tema claro/escuro manual (antes só seguia o SO).

**Alternador de tema**: `features/theme/theme-context.tsx` (`ThemeProvider`, contexto simples `{ theme: 'light'|'dark', toggleTheme }`) + `components/theme-toggle.tsx` (botão sol/lua, ícones `lucide-react`). Persistido em `localStorage` (`fintrack-theme`). A escolha manual tem sempre prioridade sobre `prefers-color-scheme` — em `index.css`, os valores dark passaram a estar tanto em `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {...} }` (sem escolha manual, segue o SO) como em `:root[data-theme="dark"] {...}` (escolha manual, gera sempre). **Sem flash do tema errado ao carregar**: um pequeno `<script>` inline no `<head>` do `index.html` aplica o `data-theme` guardado *antes* do primeiro paint — sem isto, a página pintava sempre com o tema do sistema por uma fração de segundo antes do React montar o `ThemeProvider` e corrigir. Botão colocado no `PageHeader` partilhado (novo, ver abaixo) e nas páginas sem esse cabeçalho (landing, login, registo, dashboard).

**`PageHeader` novo** (`components/page-header.tsx`): as 9 páginas internas (contas, categorias, transações, orçamentos, recorrentes, objetivos, histórico, agregado, definições) tinham todas o mesmo bloco de cabeçalho repetido byte-a-byte (título + link "Voltar ao painel"). Extraído para um componente partilhado com animação de entrada e o alternador de tema — reduz duplicação e significa que qualquer ajuste futuro ao cabeçalho (ex: mais um botão) só precisa de ser feito uma vez.

**Tokens semânticos propagados**: as 9 páginas + `dashboard.tsx` + `error-boundary.tsx` tinham ~90 ocorrências de classes `slate-*`/`green-600`/`red-600`/`indigo-500` diretas (herdadas de antes da Fase 16), que não respeitavam a escolha manual de tema (só o `prefers-color-scheme`, via `dark:`). Substituídas por scripts de replace com padrões exatos (não regex genérica, para não arriscar apanhar strings parecidas por engano) pelos tokens semânticos (`text-ink-muted`, `border-border`, `bg-surface-hover`, ...) e pelas cores funcionais alinhadas (`text-emerald-500`/`text-red-500` para valores positivos/negativos, substituindo `green-600`/`red-600`; `bg-accent` a substituir `bg-indigo-500` na barra de progresso dos objetivos, ligando-a à cor de marca).

**Animações de "atenção ao detalhe" acrescentadas**:
- Todas as listas (contas, categorias, transações, orçamentos, recorrentes, objetivos, membros do agregado) — as linhas entram com um `stagger` (fade + deslocamento vertical, atraso crescente por índice) em vez de aparecerem todas de repente.
- Barras de progresso (orçamentos, objetivos) animam do 0% até ao valor real ao carregar, em vez de aparecerem já preenchidas.
- Gráficos Recharts (histórico, dashboard) passaram a usar `var(--border)`/`var(--surface-raised)`/`var(--ink-muted)` nos eixos/grelha/tooltip em vez de cores `slate` fixas — antes ficavam ilegíveis em modo escuro (grelha quase invisível, tooltip com fundo claro a destoar).
- Login/registo ganharam a mesma entrada suave da landing (fade + subida), com o logótipo da marca acima do cartão.

**Bug real encontrado pelos próprios testes E2E**: a barra de progresso animada dos orçamentos (`ProgressBar`, 0.6s) fez o `budgets.spec.ts` falhar de forma consistente — o teste lia o atributo `style` da barra logo a seguir à criação do orçamento, e por vezes apanhava um frame a meio da animação em vez do valor final (`width: 30%`). **Corrigido em dois níveis**: (1) `ProgressBar`/`GoalProgress` passaram a respeitar `useReducedMotion()` como todo o resto da app — faltava nestas duas antes; (2) `playwright.config.ts` passou a correr com `reducedMotion: 'reduce'` globalmente, o que desliga todas as animações Framer Motion (que já respeitam essa preferência) durante os testes — evita esta classe inteira de flakiness para qualquer animação futura, e testa de borla que as animações respeitam mesmo essa preferência de acessibilidade. Uma segunda falha relacionada (`budgets.spec.ts` procurava a classe `bg-green-600`, que passou a `bg-emerald-500`) era só o teste desatualizado — corrigido o seletor.

**Testes**: novo `theme.spec.ts` — alterna o tema, confirma que o atributo `data-theme` muda, e que sobrevive a um reload da página (persistência).

**Validação visual**: sem a extensão do browser disponível (continuou desligada nesta sessão) — usado o Chromium do Playwright para gerar screenshots guardados em disco, em modo claro e escuro, confirmando visualmente Orçamentos, Transações, Definições (incluindo o próprio alternador a mudar de escuro para claro ao vivo) e Contas. Também confirmado por `getComputedStyle` que o texto tem sempre a cor `--ink` esperada com opacidade 1 (uma leitura visual inicial de um screenshot comprimido tinha parecido mais esbatida do que realmente é).

---

## 2026-08-29 — Reformulação visual, parte 1: tokens, componentes partilhados, landing page, animações

A pedido do utilizador ("não estou a gostar do design... quero mais animações, uma landing page... algo chamativo, elegante"). Escolhido em conjunto: **redefinição visual completa** (não só a landing) no estilo **"fintech premium"** (referência: Linear/Stripe/Mercury). Esta entrada cobre a base construída nesta sessão — a maior parte das páginas individuais da app ainda não foi tocada uma a uma (só herdaram o levantamento dos componentes partilhados).

**Sistema de tokens** (`frontend/src/index.css`): paleta escura por omissão com equivalente claro — `--canvas`/`--surface`/`--border`/`--ink`/`--ink-muted` para superfícies e texto, `--accent` (violeta `#8c7bff` no escuro, `#6552f5` no claro) + `--accent-teal` para o gradiente de marca. Usa `@theme inline` do Tailwind v4 para gerar utilities normais (`bg-canvas`, `text-ink-muted`, `border-border`, ...) a partir de `custom properties` que mudam de valor com `@media (prefers-color-scheme: dark)` — a maioria do markup não precisa de escrever `dark:` explicitamente, é a própria variável que muda. Fontes via Google Fonts: **Inter** (corpo/UI, já estava implícito no browser) e **Space Grotesk** (títulos/display — escolhida em vez de continuar só com Inter para ter mais carácter na landing page, seguindo a orientação da skill `frontend-design` de não usar o par tipográfico "óbvio" de qualquer produto SaaS).

**Componentes partilhados redesenhados** (`components/ui/{button,card,input,label,select}.tsx`): sombras subtis, cantos mais arredondados, focus rings e hover states no novo acento. **Alavanca deliberada**: como todas as páginas já compunham a partir destes 5 ficheiros, mudar só aqui já dá um levantamento visual visível em toda a app sem tocar em cada página — confirmado no dashboard (screenshot em modo escuro) que ficou consistente com a nova paleta apesar de o próprio ficheiro `dashboard.tsx` não ter sido editado.

**Landing page nova** (`routes/landing.tsx`) — antes disto, `/` já era o dashboard (só acessível autenticado); não existia nenhuma página pública. Decisão de conteúdo/design seguindo o processo da skill `frontend-design` (brainstorm → plano de tokens/tipo/layout/assinatura → crítica → construção):
- **Assinatura visual**: em vez de formas abstratas ou estatísticas inventadas (o utilizador é um único projeto escolar/portefólio, sem base de utilizadores real para citar — inventar "10 000 utilizadors" seria desonesto), o hero mostra um cartão de extrato animado com categorias e valores reais da app (Ordenado, Renda, Alimentação, Transporte). A secção do agregado familiar tem a sua própria assinatura: duas linhas "Renda -420€" (Antonio/Teresa) a fundirem-se visualmente numa só "Renda partilhada -420€ — não -840€" — a mesma funcionalidade implementada na entrada anterior, agora mostrada como argumento de venda.
- **Copy**: sem estatísticas fabricadas, sem depoimentos falsos, sem colunas de rodapé com páginas que não existem ("Sobre nós", "Carreiras", ...) — rodapé minimalista e honesto. "Grátis, sem cartão de crédito" é literalmente verdade (não há sistema de pagamento).
- **Reestruturação de rotas**: `/` passou a ser a landing pública; o dashboard mudou para `/dashboard`. Atualizados os redirects de login/registo e os 9 links "Voltar ao painel" nas outras páginas.

**Animações** (`motion` — instalado desde a Fase 0, nunca usado até agora): entrada em stagger no hero, `whileInView` nas secções de features/agregado/CTA final, `AnimatePresence` a dar fade+slide na transição entre rotas (`App.tsx`), e um `Splash` novo (logótipo a pulsar) a substituir o texto simples "A carregar..." no arranque da sessão e no carregamento de rotas lazy.

**Problema técnico**: `<Button asChild>` (padrão Radix Slot) foi a primeira tentativa para estilizar `<Link>` como botão — mas o `Button` deste projeto é um `<button>` simples sem suporte a `asChild`/`Slot`, e adicionar `@radix-ui/react-slot` só para isto seria uma dependência a mais para uma necessidade pequena. Resolvido exportando `buttonVariants` (a função `cva` já existente) e aplicando-a diretamente como `className` do `<Link>` — sem dependências novas.

**Acessibilidade — bug real encontrado e corrigido antes de reportar como terminado**: as animações `whileInView` (features, fusão do agregado, CTA final) só tinham a guarda de `prefers-reduced-motion` em duas de várias ocorrências. Descoberto ao validar com `page.emulateMedia`/`browser.newContext({ reducedMotion: 'reduce' })` no Playwright — sem a guarda, essas secções ficavam a 0% de opacidade indefinidamente para quem tem a preferência de movimento reduzido ativa (nunca chegam a "entrar" na vista de forma visível o suficiente, ou dependem de um evento de scroll que pode não bastar). Corrigido aplicando `useReducedMotion()` de forma consistente em todos os `motion.*` da landing, do `Splash` e da transição de página em `App.tsx`.

**Validação visual** (sem a extensão do browser disponível nesta sessão — usado o Chromium do Playwright diretamente para tirar screenshots e guardá-las em disco): confirmado visualmente em modo claro, modo escuro, viewport mobile (375px, sem overflow horizontal) e `prefers-reduced-motion: reduce` (conteúdo visível de imediato, sem esperar por scroll). Um "corte" na caixa do agregado familiar num screenshot `fullPage` acabou por ser um artefacto de stitching do Playwright com o nav `sticky` (confirmado tirando um screenshot normal, sem `fullPage`, da mesma secção) — não um bug real de layout.

**Custo aceite**: o bundle inicial (chunk `index-*.js`) cresceu de ~290 kB para ~416 kB gzip, porque a transição de página (em `App.tsx`, carregado sempre) agora importa `motion/react` — deixou de poder ser só uma dependência da landing page (que continua no seu próprio chunk lazy, ~9 kB). Aceite conscientemente: as transições de página pedidas afetam a app toda, não só a landing.

**Testes**: 2 novos testes E2E (`landing.spec.ts`) — visitante não autenticado vê a landing com CTAs corretos; utilizador autenticado que visite `/` é redirecionado para `/dashboard`. Os testes existentes foram atualizados para `/dashboard` em vez de `/`.

**O que fica para a parte 2** (ver "Próximos passos" no topo): propagar os tokens semânticos (`text-ink-muted`, `border-border`, ...) às páginas individuais, que ainda usam `slate-*`/`dark:` diretamente; animações de entrada para listas/cards dentro da app (contas, transações, ...); possivelmente rever as cores do Recharts (dashboard/histórico) para conversar com a nova paleta de acento.

---

## 2026-08-28 — Fase 13: suite Playwright E2E, e um bug real de concorrência encontrado por ela

**Decisão**: `@playwright/test` instalado como dev dependency do frontend (`frontend/e2e/`, `playwright.config.ts`, script `npm run test:e2e`). 5 testes cobrindo os fluxos combinados no roadmap: registo→dashboard, login, criar conta+categoria+transação e ver o saldo, criar orçamento e ver a barra de progresso, dashboard com dados corretos após criar transações. Correm contra a stack real do `docker compose up -d` (não há mock de API nem de browser) — coerente com a decisão já tomada na Fase 0 de usar Postgres real em vez de Testcontainers.

**Bug real encontrado ao escrever os testes — não era um problema no teste**: os testes que navegavam entre páginas com `page.goto()` (recarregando a SPA) ficavam por vezes presos na página de login, apesar do login/registo ter tido sucesso. Investigação: o `AuthProvider` chama `refreshSession()` ao montar (para renovar a sessão a partir do refresh token no cookie httpOnly). O `StrictMode` do React invoca esse `useEffect` duas vezes em modo de desenvolvimento (o `vite dev` usado tanto localmente como no `docker-compose` atual — as Dockerfiles de produção da Fase 15 ainda não existem). Isso disparava **duas chamadas concorrentes a `/api/v1/auth/refresh` com o mesmo cookie**. O backend implementa rotação de refresh tokens com deteção de reutilização (Fase 2): cada uso troca o token por um novo e revoga o antigo; se um token já revogado for reutilizado, assume-se roubo e **revoga-se toda a família de tokens do utilizador**. A segunda chamada concorrente acabava por usar o token que a primeira já tinha rodado, acionando essa deteção e terminando a sessão à força — o utilizador aparecia subitamente deslogado sem ter feito nada de errado.

**Porquê isto importa além dos testes**: o mesmo cenário podia acontecer em uso real sem StrictMode — por exemplo, várias queries do TanStack Query em paralelo (o dashboard faz 3 pedidos simultâneos) a apanharem 401 ao mesmo tempo por o access token ter expirado durante uso ativo, cada uma chamando `refreshSession()` de forma independente pelo interceptor de 401 em `api/client.ts`.

**Correção**: `refreshSession()` em `frontend/src/api/client.ts` agora guarda a promise do pedido em curso (`inFlightRefresh`) e devolve-a a qualquer chamada concorrente, em vez de disparar um novo `fetch`. Chamadas simultâneas passam a partilhar o mesmo pedido de rede, e só uma chega ao backend de cada vez — elimina a corrida sem tocar na lógica de rotação/deteção de reutilização do backend (que continua válida e é a defesa real contra roubo de token). Confirmado com 13 execuções consecutivas da suite completa sem falhas depois da correção (antes: falhava de forma intermitente, ~1 em cada 3-4 execuções).

**Nota para a apresentação**: bom exemplo de um bug de concorrência real (race condition) só visível sob condições específicas (StrictMode + rede rápida o suficiente para a corrida acontecer), encontrado por escrever testes end-to-end que exercitam a app como um utilizador real — e não pelos 190 testes unitários/integração, que usam `TestClient` sequencial e nunca disparam pedidos verdadeiramente concorrentes.

**Higiene de dados**: a suite cria utilizadores reais (`@example.com`, domínio reservado pela IANA para testes — TLDs como `.test`/`.local` são rejeitados pelo `email-validator` do backend por serem "reserved/special-use") contra o Postgres do `docker-compose`. Estes ficam na base de dados após cada corrida; nesta sessão isto chegou a acumular 100+ utilizadores de teste e partiu um teste de segurança que assume a tabela `refresh_tokens` vazia (`test_refresh_token_is_stored_hashed_not_in_plaintext`) — resolvido apagando os utilizadores de teste (`DELETE FROM users WHERE email LIKE '%@example.com'`, cascata limpa tudo). Não há limpeza automática — a limpar manualmente sempre que a suite E2E correr muitas vezes seguidas contra a mesma base de dados local.

**CI**: adicionado job `e2e` a `.github/workflows/ci.yml` (sobe Postgres + backend `uvicorn` + frontend `vite dev`, espera ambos ficarem prontos com `wait-on`, corre `npm run test:e2e`, publica o relatório do Playwright como artefacto se falhar). **Ainda não validado num push real** — só corrido localmente.

---

## 2026-08-28 — Fase 15: Dockerfiles de produção

**Decisão**: `backend/Dockerfile.prod` e `frontend/Dockerfile.prod`, ambos multi-stage, mais `docker-compose.prod.yml` na raiz e `.env.prod.example` a documentar as variáveis necessárias.

- **Backend**: stage 1 usa `uv sync --frozen --no-dev` para instalar só dependências de produção (sem pytest/ruff/httpx); stage 2 copia `.venv` + código para uma imagem `python:3.12-slim` limpa, sem `uv`. Corre como utilizador dedicado (`appuser`), não root — o processo não precisa de escrever em disco (a única persistência é o Postgres), por isso não há razão para correr como root. `CMD` faz `alembic upgrade head && exec uvicorn ... --workers ${UVICORN_WORKERS:-2}` — as migrações aplicam-se no arranque do próprio container, sem um passo de deployment separado (razoável a esta escala: um único container de backend, sem deploys concorrentes a disputar a mesma migração). Optou-se por `uvicorn --workers` nativo em vez de acrescentar `gunicorn` como gestor de processos por cima — menos uma dependência para explicar na defesa, e o Docker já trata de reiniciar o container se o processo morrer (`restart: unless-stopped`), que é o principal motivo para gunicorn existir nalguns setups.
- **Frontend**: stage 1 (`node:22-slim`) corre `npm run build`; stage 2 (`nginx:1.27-alpine`) serve só os ficheiros estáticos resultantes, com `nginx.conf` a fazer fallback de SPA (`try_files ... /index.html`, necessário porque o `react-router-dom` faz routing no cliente) e cache agressivo para `/assets/` (os nomes dos ficheiros têm hash do Vite, um build novo nunca reutiliza um nome antigo).
- **`VITE_API_URL` é um build arg, não uma env var do container final** — o Vite embebe variáveis `VITE_*` no bundle em tempo de build, o browser nunca as lê em runtime. Isto significa que mudar a URL da API a sério exige reconstruir a imagem do frontend, não só reiniciar o container — documentado no README e no `.env.prod.example` para não ser uma surpresa.
- **`docker-compose.prod.yml`** difere do de desenvolvimento em: Postgres sem porta publicada ao host (só o backend lhe fala, dentro da rede do Compose); `ENVIRONMENT=production` (ativa cookie `Secure` e a validação que recusa um `SECRET_KEY` com cara de placeholder); todas as variáveis sensíveis usam a sintaxe `${VAR:?mensagem}` do Compose, que falha o `up` com uma mensagem clara em vez de arrancar com uma string vazia se `.env.prod` não estiver preenchido.

**Problema encontrado ao escrever isto — sintaxe YAML**: `${VAR:?mensagem com dois pontos: assim}` sem aspas partia o parser do Compose ("mapping values are not allowed in this context") porque o `: ` dentro da mensagem de erro era lido como um novo par chave-valor do YAML. Resolvido pondo aspas duplas à volta do valor inteiro (`"${VAR:?mensagem}"`) e evitando dois-pontos dentro das mensagens.

**Validação manual completa** (não só "deve funcionar"): build das duas imagens, `up` com um `.env.prod` de teste, confirmado por `docker compose ps` que os 3 serviços ficam `healthy`, `curl /health` do backend a devolver `"environment":"production"`, `curl /health` do nginx do frontend, `GET /` e `GET /transacoes` (rota de cliente) a devolverem 200 pelo nginx (fallback de SPA a funcionar), registo de utilizador end-to-end com sucesso (confirma que as migrações correram), e o `Set-Cookie` do login a incluir mesmo `Secure` (confirma `ENVIRONMENT=production` a ser lido corretamente). Feito com um nome de projeto Compose isolado (`-p fintrack-prod-test`) para não misturar o volume do Postgres de produção com o de desenvolvimento — a primeira tentativa, sem isolar o projeto, reutilizou sem querer o volume `postgres_data` do dev (mesma password antiga já gravada no volume, `POSTGRES_PASSWORD` novo ignorado) e falhou a autenticação; ficou claro que sem `-p` os dois compose files partilham o mesmo *namespace* do Compose (nome da pasta) e portanto os mesmos volumes/redes por omissão.

**Efeito secundário encontrado e corrigido**: a primeira build de teste (antes de isolar o projeto) sobrescreveu as tags de imagem `projetofinal-backend`/`projetofinal-frontend` com o conteúdo dos `Dockerfile.prod` — o `docker compose up -d` do ambiente de **desenvolvimento** seguinte reutilizou essas imagens em vez de reconstruir a partir dos `Dockerfile`s de dev, o que teria deixado o dev a correr nginx/uvicorn sem reload sem ninguém perceber porquê. Resolvido com `docker compose build --no-cache` antes de repor o ambiente de dev, e confirmado com a suite Playwright + pytest completos a passar depois. **Lição registada**: sempre que se testar `docker-compose.prod.yml` localmente na mesma pasta do dev, usar `-p <nome-diferente>` desde o início (build incluído), nunca só no `up`.

**Alternativa considerada e rejeitada**: reverse proxy (nginx-proxy, Caddy) com TLS automático incluído nesta stack. Rejeitado por âmbito — este projeto não tem um domínio público real para certificar, e adicionar TLS "de mentira" só para a demo não ensinaria nada de novo que já não estivesse coberto pela decisão de arquitetura geral (mantido simples, documentado como responsabilidade da infraestrutura de deploy real).

---

## 2026-08-28 — Fase 16: Settings, error boundary, code-splitting, responsividade

Última fase do roadmap principal — fecha o projeto ao nível de "produto acabado", não só "funcionalidades todas implementadas".

**Settings (`PATCH /users/me` + UI)**: schema `UserUpdate` novo em `app/schemas/user.py`, serviço fino `user_service.update_profile`, rota `PATCH /users/me` em `app/api/v1/users.py`. Diferença deliberada face ao padrão de `AccountUpdate`/`CategoryUpdate` (edição campo-a-campo, `None` = "não mexer"): aqui `name` e `currency` são **obrigatórios** no payload, porque a página de Settings submete sempre o formulário completo de uma vez, nunca um campo isolado — `None` só faz sentido para `monthly_income`, e aí tem significado de domínio real ("sem rendimento definido"), não "não enviado". 6 testes novos em `tests/api/test_auth.py` (auth+users vivem no mesmo ficheiro por já usarem os mesmos fixtures de registo). No frontend: `AuthContext` ganhou `updateUser()` para propagar o resultado do PATCH para toda a app sem depender de um refresh de página (o nome no header do dashboard atualiza-se de imediato). **Correção a meio da escrita**: o texto de ajuda inicial do campo "Rendimento mensal" dizia que era "usado para calcular a taxa de poupança do dashboard" — falso, essa taxa (`savings_rate` em `dashboard_service.py`) usa sempre a receita real das transações, nunca `User.monthly_income` (que não tem nenhum consumidor ainda, é só um dado guardado). Corrigido antes de ficar por explicar mal na defesa.

**Bug de responsividade real encontrado a testar no browser** (não só "parece que dá"): o header do dashboard tinha `<nav className="flex gap-4">` sem `flex-wrap` dentro de um `<div className="flex items-center gap-4">` também sem wrap — com 9 links de navegação (o 9º, "Definições", foi o que empurrou o total além da largura disponível), num ecrã de 375px de largura isto causava overflow horizontal de quase o dobro da viewport (`scrollWidth` 849 vs `clientWidth` 485, confirmado via `document.documentElement.scrollWidth`). Corrigido com `flex-wrap` no `nav` e no `div` que o envolve — os links passam a quebrar em várias linhas em vez de forçar scroll lateral. Testadas todas as 11 rotas protegidas a 375px de largura depois da correção (`scrollWidth === clientWidth` em todas) — nenhuma outra página tinha o mesmo problema, todas já usavam grids responsivos (`sm:grid-cols-2`, `flex-col sm:flex-row`) desde que foram construídas.

**Lacuna de loading/erro encontrada**: `routes/history.tsx` (Fase 11) nunca tinha estados de `isLoading`/`isError` — as duas queries (`analytics-comparison`, `analytics-trend`) eram usadas só com `data &&`, por isso um erro de rede ficava completamente silencioso (nem card, nem mensagem) e um carregamento lento mostrava um ecrã vazio sem indicação nenhuma, ao contrário de todas as outras páginas do projeto (accounts/categories/transactions/budgets/recurring/goals/household já seguiam o padrão "A carregar..."/"Não foi possível carregar..." desde que foram escritas). Corrigido para seguir o mesmo padrão. **Decisão consciente de não adicionar um estado "vazio"** para o histórico: ao contrário de listas (orçamentos, objetivos), os endpoints de analytics devolvem sempre um objeto com todos os meses preenchidos a zero quando não há transações — "zero" é um valor de dados legítimo aqui, não equivalente a "sem dados", por isso mostrar €0,00 nos cartões e um gráfico plano é o comportamento correto, não uma lacuna.

**Code-splitting por rota**: todas as páginas em `App.tsx` passaram a `React.lazy(() => import(...).then(m => ({ default: m.XxxPage })))` (o `.then` é necessário porque as páginas usam `export function`, não `export default` — `React.lazy` exige que a promise resolva para `{ default }`). Resultado: o chunk inicial caiu de ~866 kB para ~290 kB, e o Recharts (~305 kB, usado só em dashboard/histórico) passou a carregar apenas quando essas rotas são visitadas — o aviso do `vite build` sobre "chunks maiores que 500 kB" desapareceu. `<Suspense>` à volta de `<Routes>` com um fallback simples ("A carregar...").

**React error boundary**: componente de classe `ErrorBoundary` (único jeito de apanhar erros de render em React — não há equivalente em hooks) a envolver toda a app em `App.tsx`, por fora do `AuthProvider`/`BrowserRouter`. Sem isto, um erro não tratado em qualquer página deixava a SPA inteira em branco, sem qualquer forma de recuperar sem um refresh manual da URL. **Validado de propósito, não só lido**: `throw new Error(...)` colocado temporariamente no topo de `DashboardPage`, confirmado no browser que a UI de fallback aparece em vez de página em branco, revertido de seguida.

**README**: nova secção "Funcionalidades" (lista o que a app faz, para quem chega ao repositório sem contexto) e "Estrutura" atualizada com os `Dockerfile.prod` e `docker-compose.prod.yml` da Fase 15.

**Validação final**: 195 testes backend, `ruff` limpo, `oxlint`/`build` do frontend limpos, 6 testes Playwright (5 anteriores + `settings.spec.ts` novo) a passar de forma consistente (3 execuções seguidas sem falhas).

---

## 2026-08-22 — Definição da arquitetura inicial

**Decisão**: Monólito modular (FastAPI em camadas `api → schemas → services → repositories → models → db`) + React SPA separado, comunicando por REST/JSON. Sem microservices, sem Redis/Kafka.

**Porquê**: o objetivo é aprender fundamentos sólidos de full-stack, não distribuição de sistemas. Um monólito bem organizado em camadas já ensina separação de responsabilidades (routing vs. regras de negócio vs. acesso a dados) sem a complexidade operacional de múltiplos serviços — complexidade essa que, além de não ser exigida pela escala da aplicação (uso pessoal, um utilizador de cada vez), tornaria a defesa oral muito mais difícil de justificar ("porque é que uma app de finanças pessoais precisa de Kafka?").

**Alternativas consideradas**: nenhuma alternativa séria de arquitetura foi ponderada além do monólito modular — dado o âmbito do projeto (final de curso + portfólio júnior), qualquer forma de distribuição seria overengineering claro.

---

## 2026-08-22 — Modelo de dados: `TRANSFER` como tipo de transação com conta de destino

**Decisão**: `transactions.type` inclui `TRANSFER`, com `account_id` (origem) + `destination_account_id` (destino, nullable) + `category_id` obrigatoriamente `NULL` nesse caso.

**Porquê**: o enunciado do projeto exige distinguir uma transferência entre contas próprias (ex: Millennium → Revolut) de uma despesa real. Modelar a transferência como uma variante do mesmo tipo `transaction` (em vez de uma tabela `transfers` separada) mantém uma única fonte de verdade para "tudo o que mexe em saldos de contas", simplificando queries de saldo e histórico — o custo é a necessidade de uma constraint (`CHECK`) e de lógica no service para garantir que transferências nunca entram nos totais de receitas/despesas do dashboard.

**Alternativa considerada e rejeitada**: tabela `transfers` própria, separada de `transactions`. Rejeitada por duplicar a necessidade de manter saldos de contas consistentes em dois sítios diferentes, e por complicar o histórico unificado de movimentos de uma conta.

---

## 2026-08-22 — Categorias com `type` (INCOME/EXPENSE)

**Decisão**: adicionar um campo `type` à tabela `categories`, não pedido explicitamente no enunciado inicial.

**Porquê**: transações de receita (`INCOME`) também beneficiam de categorização (ex: "Salário", "Freelance"), mas orçamentos (`budgets`) só fazem sentido para categorias de despesa. Sem este campo, a UI não teria forma de filtrar corretamente as categorias certas em cada formulário (transação de receita vs. despesa vs. orçamento).

---

## 2026-08-22 — Dinheiro: `NUMERIC(12,2)` + `Decimal`, não `float`

**Decisão**: todos os valores monetários são `NUMERIC(12,2)` no Postgres, mapeados para `Decimal` em Python.

**Porquê**: `float` usa representação binária de vírgula flutuante, que não representa exatamente a maioria dos valores decimais (ex: `0.1 + 0.2 != 0.3` em IEEE 754) — inaceitável para dinheiro. `NUMERIC` é o tipo do Postgres para aritmética decimal exata, e `Decimal` é o equivalente em Python.

**Alternativa considerada**: guardar tudo em cêntimos (`BIGINT`), abordagem usada por alguns sistemas de pagamento reais para evitar por completo qualquer questão de casas decimais. Rejeitada para este projeto por obrigar a converter mentalmente "tudo em cêntimos" em todas as camadas (schemas, cálculos de orçamento/projeções, frontend), aumentando a carga cognitiva sem benefício real à escala de uma app pessoal. `NUMERIC`/`Decimal` é o padrão mais comum e mais fácil de justificar/entender numa defesa.

---

## 2026-08-22 — Autenticação: access token em memória + refresh token em cookie httpOnly

**Decisão**: access token JWT de curta duração devolvido no corpo da resposta e guardado em memória no frontend (nunca `localStorage`); refresh token de longa duração em cookie `httpOnly`/`Secure`/`SameSite=Lax`, com hash persistido em `refresh_tokens` para permitir revogação/logout real.

**Porquê**: `localStorage` é acessível a qualquer script JavaScript a correr na página, o que o torna vulnerável a XSS (um script malicioso conseguiria roubar o token). Um cookie `httpOnly` nunca é acessível a JavaScript, só é enviado automaticamente pelo browser ao backend. Persistir o refresh token (com hash, nunca em claro) permite invalidar sessões (logout, deteção de roubo) — sem essa tabela, um JWT válido seria válido até expirar, sem forma de o revogar antes disso.

---

## 2026-08-22 — Eliminação de categorias: `RESTRICT`, não `CASCADE`

**Decisão**: categorias associadas a transações/orçamentos/despesas recorrentes não podem ser eliminadas diretamente — a API devolve `409 Conflict`. Frontend deverá oferecer reatribuição a outra categoria antes de eliminar.

**Porquê**: apagar em cascata destruiria histórico financeiro real do utilizador sem aviso. Numa aplicação de dinheiro, perder dados silenciosamente é um erro grave — prefere-se obrigar a uma decisão explícita.

---

## 2026-08-22 — Simplificações de teste face ao âmbito de um projeto final de curso

**Decisão**: testes de integração usam Postgres real via `docker-compose` (local) e serviço nativo do GitHub Actions (CI), em vez de introduzir a biblioteca Testcontainers. Playwright E2E cobre 4–6 fluxos críticos, não uma suite exaustiva.

**Porquê**: o projeto tem de ser terminável no tempo disponível para um trabalho final de curso, e cada biblioteca extra é mais um conceito a saber explicar na defesa. Testcontainers e uma suite E2E exaustiva são boas práticas em contexto profissional de maior escala, mas aqui o mesmo valor de aprendizagem (testar contra uma base de dados real, cobrir os fluxos críticos de ponta a ponta) é alcançado com menos peças móveis.

**Nota para a apresentação**: isto é um bom exemplo de trade-off consciente de engenharia — escolher a solução mais simples que ainda cumpre o objetivo, e saber justificar porque não se escolheu a mais "avançada".

---

## 2026-08-22 — Camada visual do frontend: shadcn/ui + Framer Motion + Recharts

**Decisão**: componentes base com shadcn/ui (Radix + Tailwind, código copiado para o repositório), animações com Framer Motion, gráficos com Recharts.

**Porquê**: o projeto serve também de peça de portfólio para entrada no mercado como programador júnior, pelo que a UI final deve parecer um produto real, não um CRUD académico. As três escolhas são, cada uma, a opção mais usada/reconhecida no respetivo nicho do ecossistema React — o que as torna simultaneamente fáceis de justificar numa entrevista técnica e bem documentadas para resolver problemas durante o desenvolvimento.

**Alternativas consideradas**: Nivo e visx para gráficos (mais visualmente distintos ou mais controlo via D3, respetivamente, mas mais tempo/complexidade); Tailwind puro sem biblioteca de componentes (mais controlo, mais tempo manual). Recharts e shadcn/ui foram escolhidos por equilibrarem melhor "resultado visual" vs. "tempo de aprendizagem/implementação" dentro do prazo do projeto.

---

## 2026-08-22 — Fluxo de trabalho: git/GitHub fora do âmbito do assistente

**Decisão registada**: toda a gestão de git e GitHub (init, commits, branches, push, PRs, Actions) é feita exclusivamente pelo utilizador. O assistente não executa nenhum comando `git`/`gh` a partir daqui, salvo indicação explícita em contrário numa mensagem futura.

**Porquê**: preferência explícita do utilizador — quer manter controlo total sobre o histórico do repositório e o GitHub.

---

## 2026-08-22 — Fase 0: setup do repositório

**O que foi criado**: `backend/` (FastAPI mínimo com endpoint `/health` + teste), `frontend/` (Vite + React + TypeScript + Tailwind v4, página que consome `/health`), `docker-compose.yml` (postgres + backend + frontend), Dockerfiles de dev para ambos, workflow de CI (`lint-backend` com ruff, `lint-frontend` com oxlint). Sem `git init` nem qualquer ação de GitHub — feito pelo utilizador.

**Ambiente da máquina**: esta máquina não tem Python nem Docker instalados (só Node/npm). O frontend foi instalado e verificado a construir (`npm run build`) e a passar lint (`npm run lint`) com sucesso. O backend foi escrito mas **não foi possível correr/testar** aqui — vai precisar de Python 3.12+ e [uv](https://docs.astral.sh/uv/) instalados para `uv sync` + `uv run pytest`/`uv run uvicorn`, e de Docker Desktop para `docker compose up`.

**Decisão — uv como gestor de dependências Python**: em vez de `pip` + `requirements.txt` ou Poetry. `uv` é uma ferramenta única (substitui pip, venv e pip-tools), muito mais rápida, e tornou-se a recomendação mais comum no ecossistema FastAPI em 2025/2026 — bom argumento de "ferramentas modernas" no CV. `pyproject.toml` usa `[dependency-groups]` (PEP 735) para separar dependências de produção das de desenvolvimento (`pytest`, `ruff`, `httpx`).

**Decisão — Tailwind CSS v4 via plugin do Vite**: a v4 elimina o ficheiro `tailwind.config.js`/`postcss.config.js` tradicional — basta `@import "tailwindcss";` no CSS e o plugin `@tailwindcss/vite`. Menos ficheiros de configuração para explicar.

**Decisão — CORS com origens explícitas, não wildcard**: `CORSMiddleware` está configurado com `allow_origins=["http://localhost:5173"]` (não `"*"`) porque `allow_credentials=True` (necessário mais tarde para cookies de refresh token) **não é permitido** pela especificação CORS em conjunto com `allow_origins="*"`. Ficar já com origens explícitas evita ter de voltar atrás nesta configuração na Fase 2.

**Problema encontrado e resolvido**: o template Vite gerado nesta máquina já vinha com `oxlint` em vez de ESLint (linter em Rust, mais rápido) — mantido tal como veio, cumpre o mesmo papel de "Lint" no pipeline de CI. Também apareceram dois avisos menores ao configurar o alias de import `@/*` (usado mais tarde pelo shadcn/ui): a opção `baseUrl` está deprecated no TypeScript recente (resolvido usando `paths` sem `baseUrl`) e o Vite avisou sobre uso de `__dirname` no `vite.config.ts` (resolvido trocando para `import.meta.dirname`, a forma recomendada em módulos ESM).

**Como correr** (depois de instalar Python+uv e/ou Docker): ver `README.md` na raiz do projeto.

**Revisão — o que este passo ensinou**: estrutura de projeto full-stack desde o início (backend e frontend como módulos independentes que comunicam por HTTP), configuração de CORS e porque importa, gestão de dependências moderna em Python (uv) vs. Node (npm), e a diferença entre "Dockerfile de desenvolvimento" (hot-reload, volumes montados) e "Dockerfile de produção" (build otimizado) — esta última fica para mais tarde.

---

## 2026-08-22 — Instalação do ambiente (Python, uv) e primeira validação real do backend

**Instalado**: Python 3.12.10 e uv 0.12.5, ambos via `winget` (gestor de pacotes nativo do Windows) — evita ter de descarregar instaladores manualmente e é fácil de repetir/documentar.

**Problema encontrado e resolvido — `uv sync` falhava a construir o projeto**: ao correr `uv sync` pela primeira vez, o build falhou com `Unable to determine which files to ship inside the wheel` (erro do Hatchling, o build backend declarado em `[build-system]`). Causa: o nome do projeto no `pyproject.toml` (`fintrack-backend`) não corresponde a nenhuma pasta no disco (a pasta chama-se `app/`), e o Hatchling tenta adivinhar automaticamente qual o pacote a incluir no wheel a partir do nome do projeto. Como isto é uma **aplicação** (corre com `uvicorn`), não uma **biblioteca** a ser publicada/instalada por outros via `pip install`, a correção correta não é configurar manualmente o "package discovery" do Hatchling — é dizer ao uv para nem tentar construir um pacote instalável: adicionado `[tool.uv]\npackage = false` ao `pyproject.toml`, e removida a secção `[build-system]` (deixou de ser necessária). Depois disto, `uv sync` instalou as 30 dependências sem problemas.

**Validado**: `uv run pytest` (1 teste a passar), `uv run ruff check .` (sem avisos), e o servidor real (`uv run uvicorn app.main:app`) a responder `200 OK` em `/health` com o corpo esperado.

**Nota técnica (não é um bug, só uma curiosidade de ambiente)**: nesta sessão, o `PATH` do Windows só foi atualizado no registo do sistema pelo `winget`, mas o processo de terminal usado pelo assistente já estava a correr antes disso — por isso foi preciso recarregar o `PATH` manualmente a partir do registo em cada comando (`$env:Path = ... GetEnvironmentVariable(...)`). Isto é uma particularidade de como esta sessão foi iniciada, não algo que o utilizador tenha de repetir: ao abrires um terminal novo (PowerShell, Git Bash, etc.) depois desta instalação, `python` e `uv` já vão funcionar diretamente, sem qualquer passo extra.

---

## 2026-08-22 — Docker Desktop: não foi possível instalar automaticamente

**Situação**: ao verificar os pré-requisitos, confirmou-se que o **WSL2 não está instalado** nesta máquina (`wsl --status` devolveu "não está instalado"). O comando para o instalar (`wsl --install`) precisa de privilégios de administrador e de reiniciar o computador — duas coisas que o assistente não pode/deve fazer sem o utilizador estar a acompanhar (elevação de permissões e reinício da máquina são ações que o próprio utilizador tem de autorizar/executar). Por isso esta parte ficou para o utilizador seguir manualmente (passos dados na conversa).

**Resolvido**: o utilizador instalou o WSL2 (`wsl --install`, reiniciou o PC) e o Docker Desktop. Após o reinício, a app Docker Desktop ainda não estava a correr (`docker compose up` falhava com `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` — o pipe do engine não existia porque a aplicação não tinha sido aberta). Arrancou-se a aplicação (`Docker Desktop.exe`) e, passado o tempo normal de arranque do engine (~30–60s), `docker version` já respondia com o servidor. `docker compose up -d` subiu os 3 containers com sucesso — ver "Estado atual" no topo do ficheiro.

---

## 2026-08-22 — Nova funcionalidade: Households (agregado familiar)

**Pedido do utilizador**: quer poder criar um "agregado familiar" juntando a sua conta à da mulher (ex: Antonio + Teresa), com um toggle no painel central entre vista "Individual" (só os dados próprios) e vista "Agregado Familiar" (dados combinados dos dois — rendimentos somados, etc.).

**Decisão de modelo**: contas e transações continuam sempre a pertencer ao `user_id` individual — não há "conta conjunta" real na BD. O agregado familiar é uma camada de **agregação em tempo de leitura**: três tabelas novas, `households`, `household_members` (com `UNIQUE(user_id)` — um utilizador só pertence a um agregado de cada vez) e `household_invites` (convite a um utilizador já registado, estado `PENDING/ACCEPTED/DECLINED`, nunca automático). O dashboard em modo "Agregado Familiar" identifica todos os `user_id` do agregado do utilizador atual e soma os dados de todos, em vez de filtrar só pelo utilizador autenticado.

**Porquê esta abordagem**: mantém zero alterações ao modelo já desenhado para `accounts`/`transactions`/`budgets`/etc. — cada pessoa mantém sempre o seu histórico individual privado e intacto, e a vista "Individual" nunca deixa de existir. Modelar como "conta conjunta" física (ex: uma `account` partilhada por dois `user_id`) obrigaria a repensar autorização em todas as tabelas de domínio (que hoje assumem um único `user_id` dono); a agregação em tempo de leitura evita essa reestruturação e é mais simples de justificar/testar.

**Porquê exigir aceitar convite**: juntar-se a um agregado implica expor dados financeiros pessoais a outra pessoa — não deve poder ser feito unilateralmente por quem convida.

**Roadmap**: adicionada Fase 7 "Households" (a seguir ao Dashboard v1 — faz sentido só depois de existirem contas/transações reais para agregar), fases seguintes renumeradas. Ver `docs/ARCHITECTURE.md` secções 2, 4, 5, 8 para o desenho completo (tabelas, ERD, decisão). Implementação em si fica para quando chegarmos a essa fase — por agora só o desenho ficou registado.

---

## 2026-08-22 — Fase 1: base de dados (engine/session, Alembic, modelo `User`)

**Situação encontrada**: parte do trabalho desta fase já tinha sido feita numa sessão anterior que não chegou a ficar registada no diário (o PC bloqueou a meio) — `app/db/base.py`, `app/db/session.py`, `app/models/user.py` e o esqueleto do `alembic/` (com `env.py` já a importar `Base.metadata` e `settings.database_url`) já existiam e estavam corretos face ao modelo definido no `ARCHITECTURE.md`. Faltava: gerar e aplicar a primeira migração, e configurar `pytest` para correr testes de integração contra o Postgres real (agora que o Docker já está validado).

**Feito**:
- `uv run alembic revision --autogenerate -m "create users table"` + `uv run alembic upgrade head` — tabela `users` criada no Postgres do `docker-compose` (confirmado via `psql \d users`).
- Reorganizados os testes para a estrutura documentada no `ARCHITECTURE.md` (`tests/unit/`, `tests/integration/`, `tests/api/`) — `test_health.py` mudou-se para `tests/api/`.
- Adicionado `tests/integration/conftest.py` com fixture `db_session`: abre uma ligação real ao Postgres, começa uma transação, e reverte-a sempre no fim do teste (mesmo em caso de erro), para os testes nunca deixarem lixo na base de dados. Precisou de um `if transaction.is_active` antes do `rollback()` porque, quando um teste força um `IntegrityError` (ex: violação de UNIQUE), o Postgres já aborta a transação sozinho — tentar reverter uma segunda vez dava um `SAWarning`.
- Adicionados `tests/integration/test_user_model.py`: cria e lê um `User` (valida UUID gerado, default `currency='EUR'`, `Decimal` a manter precisão), e um segundo teste que confirma que a constraint `UNIQUE(email)` é mesmo aplicada pela BD.

**Decisão — `alembic/versions/` excluído do ruff**: o ficheiro de migração gerado automaticamente usa `typing.Union`/`typing.Sequence` (não o estilo `X | Y` do resto do projeto) e ultrapassa o limite de 100 colunas em algumas linhas — é o template oficial do Alembic, não faz sentido reescrever à mão cada migração gerada só por estilo. Adicionado `extend-exclude = ["alembic/versions"]` ao `[tool.ruff]` no `pyproject.toml`.

**Nota**: o `.github/workflows/ci.yml` ainda só faz lint (comentário no próprio ficheiro já dizia "cresce na Fase 13 para incluir testes e build") — por isso os testes de integração desta fase só correm localmente para já, contra o Postgres do `docker-compose`; o serviço Postgres no CI fica para a Fase 13, como já estava planeado.

**Validado**: `uv run pytest` (3 testes a passar: health check + 2 testes de integração do `User`), `uv run ruff check .` (limpo).

---

## 2026-08-22 — Fase 2 (backend): autenticação — registo, login, refresh, logout

**Objetivo**: implementar o fluxo de autenticação completo definido no `ARCHITECTURE.md` — access token JWT curto em memória no frontend, refresh token de longa duração em cookie `httpOnly`, com revogação/rotação real via tabela `refresh_tokens`.

**Camadas criadas** (primeira vez que o projeto usa a estrutura completa `api → schemas → services → repositories → models`, definida na Fase 0 mas só agora preenchida):
- `app/core/security.py` — hashing de password, criar/validar JWT, gerar e fazer hash do refresh token.
- `app/core/exceptions.py` — exceções de domínio (`EmailAlreadyRegisteredError`, `InvalidCredentialsError`, `InvalidRefreshTokenError`), traduzidas para respostas HTTP só na camada `api/` (o `service` não sabe o que é um `HTTPException`).
- `app/models/refresh_token.py` + migração Alembic.
- `app/schemas/user.py`, `app/schemas/auth.py` — validação Pydantic dos pedidos/respostas.
- `app/repositories/user_repository.py`, `refresh_token_repository.py` — só queries, sem regra de negócio.
- `app/services/auth_service.py` — orquestra tudo: registar, autenticar, rodar refresh token, logout.
- `app/api/deps.py` — `get_current_user` (dependency do FastAPI que lê o header `Authorization: Bearer ...`).
- `app/api/v1/auth.py` (`/register`, `/login`, `/refresh`, `/logout`) e `app/api/v1/users.py` (`/users/me`, primeira rota protegida — prova que o mecanismo de autorização funciona de ponta a ponta).

**Decisão — registo faz login automático**: `/register` já devolve `access_token` + define o cookie de refresh, tal como `/login` — evita o utilizador ter de submeter as credenciais duas vezes seguidas (registar, depois logar) só para começar a usar a app.

**Decisão — mensagem de erro genérica no login**: `401 "Email ou password inválidos."` tanto para email inexistente como para password errada, de propósito — nunca revelar qual dos dois estava errado, para não permitir a um atacante descobrir que emails têm conta.

**Decisão — cookie de refresh restrito a `Path=/api/v1/auth`**: o cookie só é enviado pelo browser nos pedidos a `/api/v1/auth/*` (registo/login/refresh/logout), nunca nos outros pedidos à API. O access token é que vai no header `Authorization` em todos os outros pedidos. Reduz a superfície de exposição do cookie.

**Problema 1 — `passlib` incompatível com o `bcrypt` atual**: ao correr os primeiros testes, `hash_password` rebentava com `ValueError: password cannot be longer than 72 bytes`. Investigação: o `passlib` (a biblioteca que o `ARCHITECTURE.md` tinha planeado usar) não tem release desde 2020 e faz uma verificação interna de "bug de wraparound" do bcrypt usando uma password de teste propositadamente longa; versões modernas do `bcrypt` (a partir da 4.1) deixaram de truncar passwords >72 bytes silenciosamente e passaram a levantar erro — o que faz essa verificação interna do `passlib` rebentar antes mesmo de qualquer código nosso correr. Havia dois caminhos: fixar `bcrypt<4.1` (mantém `passlib`, mas prende o projeto a uma versão antiga de uma dependência de segurança) ou deixar de usar o `passlib` e chamar `bcrypt` diretamente (só precisávamos de duas funções, `hashpw`/`checkpw`). Optou-se pela segunda — mais simples, sem a camada de abstração de uma biblioteca não mantida, e resolve o problema na raiz em vez de o mascarar. Efeito secundário: como o `bcrypt` novo já não trunca silenciosamente, foi preciso adicionar `max_length=72` ao campo `password` no schema Pydantic de registo, para o próprio pedido ser rejeitado com um erro de validação claro (`422`) em vez de a app rebentar a meio do hashing.

**Problema 2 — commits dos testes de API "vazavam" para a base de dados real**: o padrão usado na Fase 1 para os testes de integração (abrir uma transação e reverter sempre no fim) partia do princípio de que o código sob teste nunca chamaria `commit()`. Os endpoints de auth chamam `db.commit()` a sério (para os utilizadores/refresh tokens ficarem persistidos entre pedidos HTTP). Um `session.commit()` numa sessão ligada diretamente a uma `connection` com uma transação manual **termina essa transação externa** — ou seja, os dados de teste ficariam mesmo gravados na base de dados de desenvolvimento, e testes a correr outra vez podiam colidir com o `UNIQUE(email)`. Corrigido usando o modo `join_transaction_mode="create_savepoint"` do SQLAlchemy 2.0: cada `commit()` do código da aplicação passa a libertar/reabrir um `SAVEPOINT` em vez de terminar a transação externa, que só é mesmo revertida no fim de cada teste. Documentado com um comentário no `tests/conftest.py` — é um detalhe subtil que vale a pena saber explicar na defesa.

**Problema 3 — container Docker do backend com dependências desatualizadas**: depois de tudo passar nos testes (correndo diretamente na máquina, fora do Docker), o container `backend` continuava a rebentar com `ModuleNotFoundError: No module named 'sqlalchemy'` ao arrancar. Causa: o `docker-compose.yml` só monta `./backend/app` como volume (para hot-reload do código) — o ambiente Python (`.venv`) fica sempre preso ao que existia no momento do `docker build`, e a imagem tinha sido construída na Fase 0, antes de SQLAlchemy/Alembic/psycopg (Fase 1) e agora bcrypt/PyJWT (Fase 2) serem adicionados ao `pyproject.toml`. `docker compose up` sozinho **não** reconstrói a imagem automaticamente quando só o `pyproject.toml` muda. Resolvido com `docker compose build backend` seguido de `docker compose up -d backend`. **Lição a lembrar nas próximas fases**: sempre que se adicionar uma dependência nova ao backend, é preciso reconstruir a imagem Docker antes de testar lá — o hot-reload do volume só cobre mudanças ao código, não ao `pyproject.toml`/`.venv`.

**Validado end-to-end**: além de `uv run pytest` (14 testes: 4 de segurança unitários, 7 de API de auth incluindo rotação de refresh token e revogação, 2 de integração do modelo `User`, 1 de health check) e `uv run ruff check .` (limpo, com `extend-immutable-calls` adicionado ao `pyproject.toml` para o ruff parar de assinalar `Depends(...)` do FastAPI como bug), o fluxo completo foi testado a sério contra o container Docker real com `curl`: registo → `/users/me` com e sem token → `/refresh` (token rodado) → `/logout` (refresh token revogado). Utilizador de teste apagado da BD de desenvolvimento no fim.

**Por fazer nesta fase**: páginas de login/registo no frontend, contexto React para o access token em memória, interceptor para renovar automaticamente via `/refresh` quando o access token expira, e rotas protegidas no React Router.

---

## 2026-08-22 — Fase 2 (frontend): login, registo, rotas protegidas

**Dependências novas**: `react-router-dom`, `@tanstack/react-query`, `react-hook-form`, `zod` + `@hookform/resolvers`, `clsx`/`tailwind-merge`/`class-variance-authority` (utilitários do shadcn/ui), `lucide-react`, `motion` — todas já previstas no `ARCHITECTURE.md`.

**Estrutura criada** (primeira vez que o frontend sai do "hello world" da Fase 0):
- `src/api/token-store.ts` — o access token vive **fora da árvore React**, num módulo simples com um pequeno pub/sub (`subscribeAccessToken`). Porquê: o cliente HTTP (`src/api/client.ts`) precisa de ler/escrever o token em código que corre fora de componentes React (dentro de uma função `fetch`), e o `AuthContext` também precisa de o refletir. Um módulo à parte evita ter de passar o token manualmente por todo o lado.
- `src/api/client.ts` — wrapper à volta de `fetch` com renovação automática: se um pedido responde `401`, tenta uma vez `refreshSession()` (chama `/api/v1/auth/refresh` usando o cookie httpOnly) e repete o pedido original com o novo access token. Só falha a sério se o refresh também falhar (sessão mesmo expirada).
- `src/features/auth/` — `types.ts`, `api.ts` (chamadas HTTP), `context.ts` (o `React.Context`, à parte do provider por razões explicadas abaixo), `auth-context.tsx` (`AuthProvider`), `use-auth.ts` (hook `useAuth()`).
- `src/components/ui/` — `button.tsx`, `input.tsx`, `label.tsx`, `card.tsx`: primitivas no estilo shadcn/ui, escritas à mão (Tailwind + `class-variance-authority` para variantes) em vez de correr o CLI `shadcn add` — mais previsível de gerar via ferramentas automatizadas nesta sessão, mesmo resultado final (código copiado para o repositório, sem dependência de runtime).
- `src/routes/login.tsx`, `register.tsx` — formulários com `react-hook-form` + validação `zod`, ligados ao `useAuth()`.
- `src/routes/protected-route.tsx` — redireciona para `/login` se não autenticado; mostra um estado de "a carregar" enquanto a Fase 2 ainda está a tentar renovar a sessão a partir do cookie.
- `App.tsx` passou a ser só a configuração de rotas (`react-router-dom`); `main.tsx` ganhou o `QueryClientProvider` do TanStack Query (usado a partir da Fase 3 em diante para os pedidos de dados).

**Decisão — arranque da app tenta sempre `/refresh` primeiro**: como o access token só vive em memória, um F5 na página perdia sempre a sessão se não houvesse este passo. O `AuthProvider`, ao montar, chama `refreshSession()` uma vez; se o cookie de refresh ainda for válido, o utilizador continua autenticado sem ter de fazer login outra vez — só perde a sessão de facto quando o refresh token expira (30 dias) ou faz logout.

**Decisão — `AuthContext` (o objeto `createContext`) num ficheiro à parte do `AuthProvider`**: o `oxlint` (linter usado no projeto) avisou (`react(only-export-components)`) que um ficheiro que exporta um componente React e também um valor não-componente (o `Context`) parte o Fast Refresh do Vite (perde-se o estado do componente a cada hot-reload durante o `npm run dev`). Resolvido movendo o `Context`/tipos para `src/features/auth/context.ts`, ficando `auth-context.tsx` só com o componente `AuthProvider`.

**Simplificação consciente, a rever se vier a ser problema**: se um pedido a meio da sessão falhar a renovar (refresh token realmente expirado), o `AuthContext` só fica "desatualizado" (continua a mostrar o utilizador como autenticado) até à próxima ação que dependa da API — não há ainda um mecanismo global que force logout automático nesse caso preciso. Como só existe uma rota protegida (o dashboard placeholder) nesta fase, o impacto é mínimo; fica anotado para revisitar quando houver mais pedidos de dados espalhados pela app (Fase 3 em diante), por exemplo com um handler de erro global do TanStack Query.

**Confirmado, não assumido — como o dinheiro chega ao frontend**: testado diretamente com Python/Pydantic que um campo `Decimal` é sempre serializado como **string** em JSON (`"12.50"`, nunca `12.5` como número) — por isso `monthly_income` foi tipado como `string | null` no frontend (`features/auth/types.ts`), não `number`. Confirma na prática a decisão da secção 8 do `ARCHITECTURE.md` de nunca deixar dinheiro passar por um `number`/`float` do JavaScript.

**Validado**: `npm run build` (tsc + vite build, sem erros) e `npm run lint` (oxlint, limpo). Reconstruída a imagem Docker do frontend (mesmo motivo do backend — `docker-compose.yml` só monta `src/`/`public/` como volume, `node_modules` fica preso ao `npm ci` do `docker build`; `npm install` de pacotes novos no host nunca chega ao container sozinho). Confirmado por `curl` que o servidor Vite dentro do Docker serve a shell da SPA corretamente.

**Por verificar manualmente** (não foi possível testar visualmente num browser nesta sessão — a extensão Claude em Chrome não ficou ligada): abrir `http://localhost:5173`, confirmar que redireciona para `/login` (sem sessão), registar uma conta, confirmar que cai no dashboard já autenticado, testar "Terminar sessão", e voltar a entrar com as mesmas credenciais.

---

## 2026-08-22 — Confirmação visual do fluxo de autenticação (Claude em Chrome)

**Situação**: a extensão Claude em Chrome não estava ligada nas sessões anteriores; ligou-se nesta sessão, permitindo finalmente o teste visual do fluxo de login/registo pendente desde a Fase 2 (frontend).

**Testado end-to-end no browser real** (containers Docker, `http://localhost:5173`):
1. Acesso sem sessão a `/` → redireciona para `/login`. OK.
2. Registo de conta nova (`/registar`) → login automático, cai no dashboard placeholder já autenticado. OK.
3. Nova navegação para `/` (equivalente a F5) → sessão mantida via `refreshSession()` a partir do cookie httpOnly, sem precisar de novo login. OK.
4. "Terminar sessão" → revoga o refresh token e redireciona para `/login`. OK.
5. Login de novo com as mesmas credenciais → sucesso. OK.
6. Login com password errada → mensagem genérica "Email ou password inválidos." (nunca revela qual dos dois campos está errado, como decidido na Fase 2). OK.

**Observação (não bloqueante)**: numa das repetições do passo 3, logo a seguir ao registo, a navegação para `/` mostrou por breves instantes o formulário de `/login` em vez do dashboard, antes de eu recarregar e confirmar que a sessão afinal persistia (repetições seguintes do mesmo passo funcionaram sempre à primeira). Suspeita: possível condição de corrida entre o `Set-Cookie` do `/register` ainda não estar totalmente aplicado pelo browser e a chamada a `refreshSession()` no arranque do `AuthProvider` — não investigado a fundo porque não se repetiu de forma consistente. Fica anotado para vigiar: se voltar a acontecer de forma reprodutível numa fase futura (com mais tráfego de rede a atrasar o pedido de registo), vale a pena revisitar a ordem `register → set cookie → redirect` no backend ou adicionar um pequeno retry/espera no frontend.

**Limpeza**: utilizador de teste (`antonio.teste.fintrack@example.com`) apagado da tabela `users` no Postgres de desenvolvimento no fim (`docker compose exec postgres psql -U fintrack -d fintrack -c "DELETE FROM users WHERE email = '...'"`).

**Validado**: fluxo de autenticação da Fase 2 dado como completo e confirmado visualmente. Sem alterações de código nesta sessão.

---

## 2026-08-22 — Fase 3: Accounts (CRUD completo, backend + frontend)

**Objetivo**: primeira funcionalidade de domínio real da app — CRUD de contas financeiras (`accounts`), com `current_balance` mantido pelo service layer conforme desenhado no `ARCHITECTURE.md`.

**Backend** (segue exatamente a estrutura em camadas da Fase 2 — `api → schemas → services → repositories → models`):
- `app/models/account.py` — modelo `Account` + enum `AccountType` (`BANK`/`WALLET`/`SAVINGS`/`CREDIT_CARD`/`OTHER`). Usa `enum.StrEnum` (não `class X(str, enum.Enum)`) porque o `ruff` (regra `UP042`) sinaliza a segunda forma como obsoleta desde o Python 3.11.
- `app/schemas/account.py` — `AccountCreate`, `AccountUpdate` (todos os campos opcionais, para `PATCH` parcial), `AccountRead`.
- `app/repositories/account_repository.py` — `list_by_user`, `get_by_id_for_user` (filtra sempre por `user_id`, nunca só por `id` — é o que impede um utilizador aceder/editar contas de outro), `create`, `delete`.
- `app/services/account_service.py` — a decisão mais importante desta fase: **`update_account` nunca sobrescreve `current_balance` diretamente a partir de um novo `initial_balance`; aplica só a diferença** (`delta = novo - antigo; current_balance += delta`). Porquê: a partir da Fase 5 (Transactions), `current_balance` vai divergir de `initial_balance` à medida que transações forem lançadas. Se a edição do saldo inicial simplesmente copiasse o valor para `current_balance`, editar o nome de uma conta anos depois de criada apagaria silenciosamente o efeito de todas as transações já lançadas. Aplicar só o delta é correto tanto agora (sem transações, delta = valor novo) como mais tarde (com transações, preserva o que elas já ajustaram).
- `app/api/v1/accounts.py` — `GET/POST /accounts`, `PATCH/DELETE /accounts/{id}`, todos atrás de `get_current_user` (o mesmo dependency da Fase 2).
- Migração Alembic `create accounts table` gerada e aplicada.
- Testes (`tests/api/test_accounts.py`, 7 testes): criar conta, listar só as próprias (utilizador B não vê contas do utilizador A), o delta de `current_balance` ao editar `initial_balance`, editar nome não mexe no saldo, um utilizador não consegue editar conta de outro (`404`, não `403` — de propósito, para não revelar que o `id` existe), eliminar, e exigência de autenticação. 21 testes a passar no total (14 anteriores + 7 novos), `ruff check` limpo.

**Frontend**:
- `src/features/accounts/` (`types.ts`, `api.ts`, `schemas.ts`) e `src/routes/accounts.tsx` — primeira página a usar o TanStack Query já configurado desde a Fase 2 (`useQuery` para listar, `useMutation` + `invalidateQueries` para criar/editar/eliminar).
- Novo componente `components/ui/select.tsx` (não existia até agora) e variante `destructive` em `components/ui/button.tsx`.
- **Decisão — eliminar conta pede confirmação inline, nunca `window.confirm()`**: um `confirm()` nativo do browser bloqueia a thread de JavaScript e trava a automação por Claude em Chrome (e é geralmente pior UX/mais difícil de testar). Implementado como estado local (`confirmingDelete`) que troca os botões "Editar/Eliminar" por "Confirmar/Cancelar" na própria linha da conta.
- Rota `/contas`, protegida como o dashboard, com link a partir do dashboard ("Ver contas").

**Problema — Vite dentro do Docker não via alterações a ficheiros novos no Windows**: depois de criar `src/routes/accounts.tsx` e atualizar `src/App.tsx` com a nova rota, o browser continuava a mostrar "No routes matched location /contas" mesmo depois de recarregar a página. Diagnóstico: `docker compose exec frontend cat /app/src/App.tsx` confirmou que o ficheiro montado (bind mount `./frontend/src:/app/src`) **já tinha o conteúdo novo** — não era um problema de sincronização de ficheiros, era o `chokidar` (watcher interno do Vite) a nunca disparar o evento de mudança. Causa: bind mounts do Docker Desktop no Windows não propagam eventos `inotify` para dentro do container Linux — o ficheiro muda no disco, mas o processo dentro do container nunca é avisado, por isso o Vite continuava a servir a transformação em cache do módulo antigo. **Corrigido** adicionando `server.watch.usePolling: true` ao `vite.config.ts` (força o Vite a verificar ficheiros periodicamente em vez de esperar por eventos do SO). Como `vite.config.ts` está na raiz do `frontend/` e **não** é um caminho montado como volume (só `src/` e `public/` o são), foi preciso `docker compose build frontend` + `docker compose up -d frontend` para a mudança chegar à imagem — um `up -d` sozinho não teria bastado. **Lição a lembrar**: esta configuração já fica feita de vez (não é algo a repetir a cada fase), mas explica por que o hot-reload pareceu "não funcionar" nesta sessão — vale a pena saber explicar na defesa se surgir a pergunta sobre Docker + Windows + dev experience.

**Validado end-to-end no browser real** (Claude em Chrome, depois da correção acima): criar conta (Banco, saldo inicial 500,50 €) → aparece na lista com o saldo correto; editar saldo inicial para 600,50 € → saldo atual acompanha corretamente; eliminar com confirmação inline → volta ao estado vazio ("Ainda não tens nenhuma conta"). Utilizador de teste apagado da BD no fim.

---

## 2026-08-22 — Fase 4: Categories (CRUD completo, backend + frontend)

**Objetivo**: CRUD de categorias próprias do utilizador (`name` + `type` INCOME/EXPENSE), com `UNIQUE(user_id, name)` para evitar duplicados.

**Backend** (mesma estrutura em camadas das Fases 2/3):
- `app/models/category.py` — modelo `Category` + `CategoryType` (`enum.StrEnum`, mesma convenção da Fase 3). Campos `icon`/`color` incluídos no modelo/schema (cosméticos, conforme `ARCHITECTURE.md`) mas sem UI para os editar ainda — não há necessidade real até ao gráfico de despesas por categoria (Fase 6), por isso não se construiu um seletor de cor/ícone só por completude.
- `app/repositories/category_repository.py`, `app/services/category_service.py`, `app/api/v1/categories.py` — mesmo padrão de `list/get/create/update/delete` scoped a `user_id` da Fase 3.
- **Decisão — duplicado verificado na aplicação, não à espera do `IntegrityError` da constraint**: tal como o registo de utilizadores na Fase 2 (`get_by_email` antes de inserir), `create_category`/`update_category` verificam `get_by_name_for_user` antes de gravar, e traduzem para `409 Conflict` com mensagem clara. A `UNIQUE(user_id, name)` na BD continua a existir como rede de segurança (ex: contra condições de corrida), mas o caminho normal nunca deixa a exceção da BD chegar à API.
- **Decisão consciente — bloqueio de eliminação por "categoria em uso" ainda não implementado**: o requisito existe no `ARCHITECTURE.md` ("bloqueio de eliminação se houver transações associadas"), mas nesta fase **nenhuma tabela referencia `categories`** — `transactions`/`budgets`/`recurring_expenses` só chegam nas Fases 5/8/9, cada uma com a sua FK `ON DELETE RESTRICT`. Implementar agora um `try/except IntegrityError` para uma FK que ainda não existe seria código morto e não testável. Fica documentado no próprio `delete_category` (comentário) para ser resolvido quando a Fase 5 adicionar `transactions` — nessa altura, um `db.flush()` sobre uma categoria associada vai levantar `IntegrityError`, que passa a ser apanhado e traduzido em `409`.
- Migração Alembic `create categories table` gerada e aplicada.
- Testes (`tests/api/test_categories.py`, 9 testes): criar, duplicado do mesmo utilizador → `409`, nomes iguais entre utilizadores diferentes → permitido, listar só as próprias, editar nome, editar para um nome já usado → `409`, um utilizador não edita categoria de outro → `404`, eliminar, exigência de autenticação. 30 testes a passar no total, `ruff check` limpo.

**Frontend**: `src/features/categories/` + `src/routes/categories.tsx`, mesmo padrão da página de Contas (TanStack Query, formulário inline, confirmação de eliminação sem `window.confirm`). Rota `/categorias`, link a partir do dashboard.

**Bug de UI encontrado e corrigido — erro em linha espremia os campos do formulário**: testado no browser, ao submeter um nome duplicado a mensagem de erro entrava na mesma `flex-row` que os campos e os botões (`<form className="flex ... sm:flex-row ...">` com o erro como mais um item dessa linha) — sem `min-width`, os inputs ficavam espremidos a poucos pixels de largura (o campo "Nome" chegou a mostrar só "Al" de "Alimentação", embora o valor armazenado estivesse correto, só visualmente cortado). Corrigido em `routes/categories.tsx` e `routes/accounts.tsx` (mesmo padrão de formulário, mesmo bug nos dois): a linha `sm:flex-row` passou a conter só os campos e os botões, com a mensagem de erro fora dessa linha, numa linha própria a toda a largura por baixo. Confirmado visualmente que o layout se mantém legível mesmo com o erro visível.

**Validado end-to-end no browser real**: criar categoria "Alimentação" (Despesa) → aparece na lista; tentar criar outra igual → erro "Já existe uma categoria com este nome." visível e bem formatado; editar para "Restaurantes" → atualiza; eliminar com confirmação inline → volta ao estado vazio. Utilizador de teste apagado da BD no fim.

---

## 2026-08-22 — Fase 5: Transactions (a peça central do modelo, backend + frontend)

**Objetivo**: CRUD de transações (`INCOME`/`EXPENSE`/`TRANSFER`), com o service a manter `current_balance` das contas sempre consistente com o histórico de movimentos.

**Backend**:
- `app/models/transaction.py` — `Transaction` + `TransactionType`. FKs para `accounts`/`categories` com `ON DELETE RESTRICT` (primeira vez que essas FKs passam a existir de facto — ver "Problema/decisão" abaixo). Duas `CheckConstraint`: `amount > 0` e a forma de uma transferência (`type='TRANSFER' ⇒ destination_account_id NOT NULL AND category_id NULL`), replicando as regras já desenhadas no `ARCHITECTURE.md`.
- **Decisão — toda a validação de negócio vive no service, não replicada em dois schemas Pydantic**: `TransactionCreate` e `TransactionUpdate` são schemas "burros" (só tipos e `Field(gt=0)` no `amount`); a combinação tipo↔categoria↔conta-destino é validada uma única vez, em `_validate_combination` (`transaction_service.py`), chamada tanto por `create_transaction` como por `update_transaction`. Evitou duplicar a mesma lógica de validação em dois `model_validator` do Pydantic que facilmente divergiriam com o tempo.
- **Decisão — `TransactionUpdate` exige sempre o objeto completo, não é um PATCH parcial por campo** (ao contrário de `AccountUpdate`/`CategoryUpdate`): `type`, `category_id` e `destination_account_id` têm invariantes cruzadas — mudar de `EXPENSE` para `TRANSFER` tem de *limpar* `category_id` e *preencher* `destination_account_id` ao mesmo tempo. Um PATCH campo-a-campo tornaria ambíguo o que um `None` significa nesses dois campos (\"não mexer\" vs. \"limpar porque o novo tipo não usa isto\"). Assume-se que a UI reenvia sempre o formulário completo ao editar uma transação — é o que a UI real faz (`routes/transactions.tsx` pré-preenche o formulário todo, nunca só um campo).
- **A lógica mais delicada — `_apply_balance_effect(type, account, destination, amount, sign)`**: uma única função com `sign=+1`/`sign=-1` aplica ou reverte o efeito de qualquer tipo de transação nos saldos. `update_transaction` usa-a duas vezes: primeiro com `sign=-1` sobre as contas *antigas* da transação (antes de editar) para desfazer o efeito anterior, depois com `sign=+1` sobre as contas *novas* (podem ser as mesmas ou diferentes, se o utilizador mudar a conta). `delete_transaction` só chama a reversão. Isto garante que editar o valor, o tipo, ou até mudar de conta origem/destino nunca deixa saldos inconsistentes, sem se repetir a fórmula em três sítios.
- **Decisão/problema — FK `RESTRICT` para `accounts`/`categories` finalmente existe, e as duas exigiam tratamento de `IntegrityError` que ainda não tinha sido escrito**: até esta fase, `account_service.delete_account`/`category_service.delete_category` apagavam sem verificação nenhuma porque nenhuma tabela os referenciava ainda (documentado assim na entrada da Fase 4). Agora que `transactions.account_id`/`destination_account_id`/`category_id` existem com `ON DELETE RESTRICT`, ambos os services passaram a fazer `try: db.flush() / except IntegrityError: db.rollback(); raise AccountInUseError/CategoryInUseError`, traduzido para `409` nos routers — exatamente como já estava anotado que aconteceria. O `db.rollback()` só desfaz até ao savepoint mais recente (ver `tests/conftest.py`), não estraga a transação de teste externa.
- Nova query com `OR` no repositório (`transaction_repository.list_by_user`): filtrar por `account_id` tem de corresponder tanto a `account_id` como a `destination_account_id` — uma conta "aparece" no extrato tanto quando é origem como quando é destino de uma transferência.
- **Refactor de testes**: `_auth_headers`/`_create_account`/`_create_category` estavam a ser copiados e colados em cada novo ficheiro de teste (`test_accounts.py`, `test_categories.py`, e agora `test_transactions.py` ia ser o terceiro/quarto). Extraídos para `tests/api/helpers.py` (`register_and_get_headers`, `create_account`, `create_category`), com os ficheiros existentes atualizados para os importar em vez de duplicar.
- Testes (`tests/api/test_transactions.py`, 16 testes): INCOME aumenta saldo, EXPENSE diminui, TRANSFER move entre contas, transferência para a própria conta rejeitada, transferência com categoria rejeitada, receita sem categoria rejeitada, categoria com tipo errado rejeitada, editar valor ajusta saldo pelo delta, editar mudando de conta move o efeito da conta antiga para a nova, eliminar reverte o saldo, filtros (conta/categoria/tipo/intervalo de datas), isolamento entre utilizadores, e os dois novos `409` (conta/categoria em uso). **45 testes a passar no total**, `ruff check` limpo (incluindo troca de `HTTP_422_UNPROCESSABLE_ENTITY`, que o Starlette já marca como *deprecated*, por `HTTP_422_UNPROCESSABLE_CONTENT`).

**Frontend**: `src/features/transactions/` + `src/routes/transactions.tsx` — o formulário mais complexo até agora: campo "Categoria" ou "Conta de destino" aparece/desaparece consoante o `type` escolhido (`useWatch` do `react-hook-form`), e a lista de categorias disponíveis filtra-se pelo tipo selecionado (só mostra categorias `INCOME` quando `type=INCOME`, etc.). Validação cruzada replicada no lado do cliente com `zod` `.superRefine()` (mensagens de erro imediatas, sem esperar pela resposta do servidor) — a validação a sério continua só no backend. Cartão de filtros (conta/categoria/tipo/intervalo de datas) usa `useQuery` com a `queryKey` a incluir o objeto de filtros, para o TanStack Query re-consultar automaticamente sempre que um filtro muda.

**Bug de UI encontrado e corrigido — 409 de conta em uso não tinha para onde ir**: ao testar no browser, tentar eliminar uma conta com transações associadas falhava sem qualquer feedback visível — `routes/accounts.tsx` nunca tinha ganho o tratamento de erro de eliminação que `routes/categories.tsx` já tinha (adicionado na Fase 4, quando só categorias podiam ficar "em uso"). Corrigido com o mesmo padrão: `onError` na `deleteMutation` a guardar a mensagem num `useState` e a mostrar por baixo do nome da conta.

**Nota sobre ferramentas de teste, não sobre a app**: durante os testes manuais desta sessão, a ferramenta `get_page_text` do Claude em Chrome devolveu conteúdo desatualizado várias vezes seguidas (mostrava sempre o mesmo HTML antigo, como se a "nova transação" nunca tivesse aberto, mesmo depois de cliques bem-sucedidos). Diagnosticado com `javascript_tool` (`document.querySelector('main').innerText`, que lê o DOM ao vivo) — a app estava sempre correta, só a extração de texto de uma ferramenta é que ficava presa numa versão antiga da página nalguns momentos. Não é um bug do FinTrack; fica registado para não repetir a confusão numa sessão futura — se `get_page_text` parecer "não refletir" uma ação, confirmar com `javascript_tool`/`read_network_requests` antes de assumir um bug de UI.

**Validado end-to-end no browser real**: criado utilizador de teste com 2 contas (Millennium, Revolut) e 2 categorias (Alimentação/EXPENSE, Salário/INCOME). Despesa de 30€ → saldo da Millennium desce corretamente; transferência de 100€ Millennium→Revolut → saldos das duas contas movem-se corretamente; editar a despesa de 30€ para 50€ → saldo ajusta só pela diferença; eliminar a transferência → saldos das duas contas revertidos; filtro por tipo "Transferência" na lista funciona; tentativa de eliminar a categoria/conta em uso mostra a mensagem `409` na UI. Utilizador de teste apagado da BD no fim.

---

## 2026-08-27 — Fase 6: Dashboard v1 (resumo do mês + gráfico de despesas por categoria)

**Objetivo**: primeira vista que transforma o CRUD numa "app" — o resumo financeiro do mês selecionado, com saldo global, receitas/despesas, poupança e um gráfico de despesas por categoria.

**Decisão-chave — o dashboard é agregação em tempo de leitura, sem tabela nem migração nova**: não há tabela `dashboard_snapshots` nem colunas derivadas guardadas. O endpoint corre `SUM(...)`/`GROUP BY` sobre as `transactions` a cada pedido. Porquê: guardar totais persistidos criaria uma segunda fonte de verdade que teria de ser mantida em sincronia a cada `create`/`update`/`delete` de transação (e a cada edição de saldo de conta) — exatamente o tipo de duplicação que o `ARCHITECTURE.md` já rejeitou para `budgets` (secção 4). À escala desta app (uso pessoal, poucas centenas de transações por ano) uma agregação por pedido é instantânea e sempre correta. É o mesmo raciocínio que vai valer para os `budgets` (Fase 8) e o modo "Agregado Familiar" (Fase 7).

**Backend** (segue as camadas habituais, mas o `repository` aqui só tem queries de agregação, e o `service` não muta nada — nenhum `db.commit()` no router):
- `app/schemas/dashboard.py` — `DashboardSummary` + `CategoryExpense`. `savings_rate` é `float | None` (não `Decimal`): é um rácio para exibição, não um valor monetário, e `None` quando não houve receitas no mês (dividir por zero não tem significado útil). Todo o resto continua `Decimal`.
- `app/repositories/dashboard_repository.py` — `total_balance` (soma de `accounts.current_balance`, **não** filtrada por mês — é a fotografia "agora"), `sum_amount_by_type` (receitas/despesas do mês) e `expenses_by_category` (`JOIN categories` + `GROUP BY` + `ORDER BY SUM DESC`). Só `EXPENSE` entra no gráfico; `INCOME` e `TRANSFER` ficam de fora.
- **Decisão — intervalo de mês semi-aberto `[dia 1, dia 1 do mês seguinte[`** em `_month_bounds`, em vez de calcular "o último dia do mês": evita ter de saber se o mês tem 28/29/30/31 dias. O "mês seguinte" trata a passagem de dezembro→janeiro incrementando o ano.
- **Problema — `COALESCE(SUM(...), 0)` devolve `0` (inteiro), não `0.00`**: quando não há transações, o Postgres devolve o literal inteiro do `COALESCE`, e a API respondia `"0"` em vez de `"0.00"` (inconsistente com o resto, e os testes apanharam-no). Corrigido com um helper `_money()` no service que faz `.quantize(Decimal("0.01"))` a todos os totais antes de construir o schema.
- `app/api/v1/dashboard.py` — `GET /api/v1/dashboard`, parâmetro opcional `month` (qualquer dia do mês, formato ISO; omitido = mês atual). Registado no `main.py`.
- Testes (`tests/api/test_dashboard.py`, 8 testes): dashboard vazio de utilizador novo, totais + taxa de poupança, transferências ignoradas nos totais mas refletidas no saldo global, só conta o mês selecionado, `expenses_by_category` agrupado e ordenado, default para o mês atual, isolamento entre utilizadores, exige autenticação. **53 testes a passar no total**, `ruff` limpo.

**Frontend**:
- Dependência nova: **Recharts** (`npm install recharts`) — a biblioteca de gráficos já prevista no `ARCHITECTURE.md`. Imagem Docker do frontend reconstruída (mesmo motivo das fases anteriores: `node_modules` fica preso ao `docker build`, só `src/` é volume).
- `src/features/dashboard/` — `types.ts`, `api.ts`, e `month.ts` (utilitários de navegação entre meses: `startOfMonth`/`addMonths`/`toIsoDate`/`monthLabel`, **sempre em hora local** — `toISOString()` converte para UTC e podia saltar um dia perto da meia-noite).
- `src/routes/dashboard.tsx` reescrito (era só um placeholder): cabeçalho com navegação (Contas/Categorias/Transações) + terminar sessão, navegador de mês (‹ ›, botão "Mês atual", seta "seguinte" desativada no mês corrente), 4 cartões de estatística (saldo global, receitas, despesas, poupança líquida + % em subtítulo), e um gráfico donut (Recharts `PieChart`) com uma legenda-lista ao lado a mostrar valor e % por categoria.
- **Decisão — paleta de cores de recurso no frontend**: o campo `categories.color` existe no modelo mas ainda não há UI para o editar (adiado desde a Fase 4). Enquanto isso, o gráfico usa uma paleta fixa de 8 cores indexada pela ordem da categoria. Quando a Fase 4 ganhar o seletor de cor, `item.color ?? FALLBACK[i]` já usa a cor real automaticamente.
- **Nit corrigido no browser**: o rótulo do mês vinha "Agosto De 2026" (a classe Tailwind `capitalize` põe maiúscula em *cada* palavra). Trocado por capitalizar só a primeira letra em JS → "Agosto de 2026".

**Validado end-to-end no browser real**: utilizador de teste com 2 contas (saldo inicial 1000 + 200), 3 categorias, e no mês atual: receita 2000, despesas 320,50 (Alimentação) + 90 (Transporte), transferência 150 entre contas. Dashboard mostrou saldo global 2789,50 € (inclui a transferência, que não mexe nos totais de receita/despesa), receitas 2000,00 €, despesas 410,50 €, poupança 1589,50 € (79,5%), e o donut com Alimentação 78% / Transporte 22%. Navegar para o mês anterior → tudo a zero + estado vazio "Sem despesas registadas neste mês", saldo global mantém-se (não é do mês). Utilizador de teste apagado da BD no fim.

**Bundle**: o `vite build` passou a avisar que o chunk único ultrapassa 500 kB (efeito do Recharts). Não se fez nada nesta fase — code-splitting por rota fica para o polish (Fase 16), onde faz mais sentido tratar disto de uma vez para toda a app.

---

## 2026-08-27 — Fase 7: Households (agregado familiar)

**Objetivo**: permitir juntar as finanças de duas (ou mais) pessoas num "agregado familiar", com um toggle no dashboard entre a vista individual e a vista combinada.

**Decisão central (já estava no `ARCHITECTURE.md`, agora implementada) — agregação em tempo de leitura, zero alterações às tabelas de domínio**: `accounts`/`transactions`/`categories` continuam a pertencer sempre a um `user_id` individual. Não há "conta conjunta". O agregado é só uma camada de leitura: quando o dashboard é pedido com `?scope=household`, o service resolve todos os `user_id` do agregado (via `household_members`) e soma os dados de todos. A vista "Individual" nunca desaparece, e o histórico de cada pessoa mantém-se privado.

**Impacto no código da Fase 6**: `dashboard_repository` deixou de receber um `user_id` e passou a receber `user_ids: Sequence[uuid.UUID]` (`WHERE user_id IN (...)`). Para a vista individual a lista tem um elemento; para o agregado tem N. A query é exatamente a mesma — foi a mudança mínima para suportar as duas vistas. O `DashboardSummary` ganhou um campo `scope` que ecoa a vista devolvida: se pedires `household` sem pertenceres a um agregado, o service cai graciosamente em `individual` e di-lo na resposta (a UI só mostra o toggle quando há agregado, mas a API não deve rebentar se for chamada à mão).

**Modelo de dados** (migração `b280080ec37d`):
- `households` (`name`, `created_by`).
- `household_members` — **`UNIQUE(user_id)`**, não `UNIQUE(household_id, user_id)`: garante que cada pessoa só pertence a um agregado de cada vez, o que elimina qualquer ambiguidade no toggle ("qual agregado mostrar?").
- `household_invites` — estado `PENDING/ACCEPTED/DECLINED/CANCELLED`. **Índice único parcial** `WHERE status = 'PENDING'`: no máximo um convite pendente para a mesma pessoa no mesmo agregado, mas é possível reconvidar quem recusou (o convite antigo fica `DECLINED`, não conta). O `alembic revision --autogenerate` apanhou o `postgresql_where` corretamente a partir do `Index(..., postgresql_where=text(...))` no modelo — não foi preciso editar a migração à mão.
- FKs todas `ON DELETE CASCADE` (a partir de `households` e de `users`) — apagar um agregado leva membros e convites com ele; apagar um utilizador idem. Confirmado na prática: apagar o utilizador criador limpou as 3 tabelas sem órfãos.

**Decisões de regras de negócio**:
- **Criar um agregado torna o criador membro automaticamente** (não faria sentido um agregado sem ninguém).
- **Qualquer membro pode convidar** (não só o criador) — simplicidade; a app é para uso familiar, não há hierarquia a modelar.
- **Convite é sempre a um email já registado** — o pedido leva o email, o service resolve para `user_id` (`404` se não existir). Não há convites a "pessoas que ainda não têm conta" (fora do âmbito).
- **Juntar-se exige aceitar explicitamente** — expor dados financeiros a outra pessoa nunca pode ser unilateral.
- **Ao aceitar um convite, os outros convites pendentes para essa pessoa são automaticamente cancelados** — já só se pode pertencer a um agregado, os outros deixaram de fazer sentido.
- **Sair do agregado**: qualquer membro pode sair (incluindo o criador — é tratado como um membro normal). **Se o último membro sai, o agregado é apagado** (com os convites pendentes em cascata) — não fica um agregado-fantasma na BD.
- Validações de convite → `409` com mensagem clara: a si próprio, a quem já é membro, a quem já está noutro agregado, convite duplicado pendente. Verificadas em código (como as categorias na Fase 4), com o índice parcial só como rede de segurança.

**Camadas** (mesmo padrão das fases anteriores): `models/household.py`, `schemas/household.py`, `repositories/household_repository.py`, `services/household_service.py`, `api/v1/households.py`. O service tem dois helpers `_build_household_read`/`_build_invite_read` que resolvem nomes/emails com lookups simples por linha — N+1 assumido de propósito (listas de 0–3 convites; "performance não é o foco", secção 3 do `ARCHITECTURE.md`), muito mais legível do que um `JOIN` triplo com `aliased(User)`.
- **Refactor de testes**: `helpers.py` ganhou `register()` (devolve o corpo completo com `user`) e `auth_headers(token)`; `register_and_get_headers` passou a ser um wrapper destes.
- Testes (`tests/api/test_households.py`, 20 testes): criar/segundo-agregado-`409`/`/me`-`404`, fluxo convidar→aceitar (os dois passam a ver o mesmo agregado), email desconhecido, convidar sem estar num agregado, auto-convite, convidar membro existente, convidar quem está noutro agregado, convite duplicado, recusar (+ reconvidar), cancelar, aceitar convite alheio, aceitar segundo convite depois de já ter aderido (+ o outro convite fica cancelado), sair (com e sem outros membros), agregado apagado ao sair o último, e **dashboard `scope=household` a somar os dois membros** (+ fallback para individual sem agregado). **73 testes no total**, `ruff` limpo.

**Frontend**: `src/features/households/` (`types.ts`, `api.ts` — `getMyHousehold` devolve `null` em vez de atirar no `404`, porque "não ter agregado" é um estado normal) + `src/routes/household.tsx` (rota `/agregado`): sem agregado → lista de convites recebidos (aceitar/recusar) + formulário de criação; com agregado → lista de membros (badge "Criador"), convidar por email, convites pendentes enviados (cancelar), e "Sair do agregado" com confirmação inline (o mesmo padrão anti-`window.confirm` das outras páginas). No `dashboard.tsx`: um toggle segmentado Individual ↔ Agregado familiar que só aparece quando `GET /households/me` devolve um agregado; o `scope` entra na `queryKey` do TanStack Query, e as mutações do agregado invalidam `['dashboard']` para a vista se atualizar ao aderir/sair.

**Validado end-to-end no browser real** com dois utilizadores (Ana e Bruno), cada um com uma conta e transações próprias:
1. Ana cria "Família Teste" → aparece como membro com badge "Criador".
2. Ana convida Bruno por email → "Convite enviado a Bruno" + entra na lista de pendentes.
3. Bruno (nova sessão) vê o convite em "Convites recebidos" → aceita → passa a ver os dois membros.
4. Dashboard da Ana: o toggle aparece; "Individual" = só os dados dela (saldo 1800 €); "Agregado familiar" = **1980 €** de saldo, receitas 1500 €, despesas 320 € (200 dela + 120 dele), donut com as duas categorias "Casa" distintas (63% / 38%).
5. Dashboard do Bruno: "Individual" = saldo 180 €, sem receitas (poupança negativa a vermelho); "Agregado familiar" = os mesmos totais combinados.

Utilizadores de teste apagados no fim; confirmado que o `CASCADE` limpou `households`/`household_members`/`household_invites` sem deixar órfãos.

**Nota de UX conhecida (não bloqueante)**: na vista de agregado, duas categorias com o mesmo nome (ex: "Casa" da Ana e "Casa" do Bruno) aparecem como duas fatias separadas no gráfico, porque são de facto categorias distintas (cada uma do seu dono). Juntá-las por nome fica para os Insights (Fase 12), se se justificar — por agora, mostrar a verdade (categorias separadas) é mais correto do que fundir coisas que o modelo trata como diferentes.

---

## 2026-08-27 — Fase 8: Budgets (orçamento mensal por categoria)

**Objetivo**: definir um limite de gasto mensal por categoria de despesa e ver o progresso (gasto / restante / %) contra as transações reais do mês.

**Decisão central (já no `ARCHITECTURE.md` secção 4, agora implementada) — `spent`/`remaining`/`percentage` NÃO são colunas**: a tabela `budgets` só guarda `category_id` + `period_month` + `amount`. O "gasto" é calculado em runtime pelo service, somando as transações `EXPENSE` dessa categoria nesse mês. Guardar o valor gasto seria uma segunda fonte de verdade que teria de ser atualizada a cada `create`/`update`/`delete` de transação — o mesmo raciocínio do dashboard (Fase 6). `remaining = amount - spent` (pode ser negativo), `percentage = spent/amount*100` (pode passar de 100). `percentage` é `float` (rácio de exibição), tudo o resto é `Decimal`.

**Refactor — `month_bounds` extraído para `app/core/dates.py`**: o cálculo do intervalo semi-aberto `[dia 1, dia 1 do mês seguinte[` estava em `dashboard_service._month_bounds` e agora é preciso também nos orçamentos. Passou para um helper partilhado `app/core/dates.month_bounds(day)`; o `dashboard_service` foi atualizado para o importar. Segunda utilização = altura certa para extrair (não antes — teria sido abstração prematura).

**Modelo** (migração `c78b7f293320`):
- `budgets` — `UNIQUE(user_id, category_id, period_month)` (um orçamento por categoria por mês), `CHECK(amount > 0)`.
- `period_month` é sempre o **primeiro dia do mês** — o service normaliza qualquer data recebida (`period_month.replace(day=1)`) antes de gravar/consultar. Simplifica as queries "orçamentos deste mês" (igualdade exata em vez de intervalo).
- FK `category_id` → `categories` **`ON DELETE RESTRICT`** (seguindo a decisão da secção 5 do `ARCHITECTURE.md`). Não foi preciso código novo: o `category_service.delete_category` já apanha qualquer `IntegrityError` de FK e devolve `409` — só se atualizou a mensagem (`"...transações ou orçamentos..."`) para não mentir sobre a causa.

**Regras de negócio**:
- **Só categorias `EXPENSE` podem ter orçamento** (`422` se for `INCOME`) — orçamentar receitas não faz sentido. É o service que valida, não um `CHECK` (precisaria de um `JOIN` na constraint).
- **Um orçamento por (categoria, mês)** — verificado em código antes de gravar (`409`), com o `UNIQUE` como rede de segurança. Mesmo padrão das categorias (Fase 4).
- **Editar só permite mudar o `amount`** — a categoria e o mês *identificam* o orçamento; mudar qualquer um deles é, na prática, criar outro. `BudgetUpdate` só tem `amount`.

**Camadas**: `models/budget.py`, `schemas/budget.py`, `repositories/budget_repository.py` (inclui `spent_by_category` — `SUM ... GROUP BY category_id` das despesas do mês, devolve `dict[category_id, Decimal]`), `services/budget_service.py`, `api/v1/budgets.py` (`GET ?month=`, `POST`, `PATCH /{id}`, `DELETE /{id}`).
- Testes (`tests/api/test_budgets.py`, 12 testes): criar (spent 0), categoria `INCOME` → `422`, categoria inexistente → `404`, duplicado → `409` (mas mês seguinte ok), `spent` reflete só as transações do mês, orçamento ultrapassado (`remaining` negativo, `percentage` > 100), listagem scoped ao mês, editar valor recalcula o progresso, eliminar, isolamento entre utilizadores, eliminar categoria com orçamento → `409`, exige autenticação. **85 testes no total**, `ruff` limpo.

**Frontend**:
- Refactor: `features/dashboard/month.ts` → **`src/lib/month.ts`** (agora partilhado com os orçamentos). Só o `dashboard.tsx` o importava; imports atualizados.
- `features/budgets/` (`types.ts`, `api.ts`) + `src/routes/budgets.tsx` (rota `/orcamentos`): navegação por mês, formulário "novo orçamento" (só mostra categorias de despesa que ainda não têm orçamento nesse mês — quando esgotam, mostra "Todas as categorias de despesa já têm orçamento para este mês"), e uma lista com **barra de progresso colorida** (verde < 80%, âmbar 80–100%, vermelho > 100%, com a barra a saturar nos 100% mas a % real no texto), texto "X disponível" / "X acima do orçamento", editar valor inline e eliminar com confirmação inline (padrão anti-`window.confirm` das outras páginas). Link "Orçamentos" na navegação do dashboard.
- Formulário sem RHF/zod (só dois campos, um `<select>` + um valor) — `useState` simples com um regex de validação do valor, como a página do agregado. `oxlint`/`build` limpos.

**Validado end-to-end no browser real**: utilizador com 2 contas/categorias de despesa (Alimentacao, Transporte) e despesas no mês (180 + 75,50 em Alimentacao; 260 em Transporte).
1. Criar orçamento Alimentacao 200 € → "255,50 € / 200,00 € · 128%", barra **vermelha** cheia, "55,50 € acima do orçamento".
2. Criar orçamento Transporte 300 € → "260,00 € / 300,00 € · 87%", barra **âmbar**, "40,00 € disponível". Form passa a "todas as categorias já têm orçamento".
3. Editar Alimentacao para 400 € → recalcula para "255,50 € / 400,00 € · 64%", barra **verde**, "144,50 € disponível".
4. Navegar para o mês seguinte → vazio + "Mês atual" aparece + form volta a oferecer as categorias.
5. Eliminar Transporte (confirmação inline) → desaparece, categoria volta a ficar disponível no form.

Utilizador de teste apagado da BD no fim.

---

## 2026-08-27 — Fase 9: Recurring Expenses (despesas recorrentes + geração de transações)

**Objetivo**: registar despesas que se repetem (renda, seguros, subscrições) e ter um mecanismo que cria as transações correspondentes sem o utilizador as lançar à mão todos os meses.

**Modelo** (migração `57804c58a457`): `recurring_expenses` com `account_id`/`category_id` (FK **`ON DELETE RESTRICT`**, como as transações), `description` (obrigatória — uma recorrência sem rótulo é inútil), `amount` (`CHECK > 0`), `frequency` (`MONTHLY`/`YEARLY`), `day_of_month` (`CHECK BETWEEN 1 AND 31`), `next_occurrence` (indexado), `active`.

**Decisão — `next_occurrence` é a fonte de verdade do "quando"; `day_of_month` só restaura o dia canónico**:
- O utilizador dá a **primeira ocorrência** como uma data (`next_occurrence`). Funciona igual para MONTHLY e para YEARLY (a tabela do `ARCHITECTURE.md` não tem `month_of_year`, e não valeu a pena adicionar uma coluna — a data inicial já fixa o mês para o caso anual).
- `day_of_month` é derivado (`next_occurrence.day`) e guardado só para uma coisa: quando um mês curto força um recuo (31/jan → 28/fev), o avanço seguinte volta ao dia canónico (28/fev → **31**/mar). A função `advance()` avança sempre a partir de `day_of_month`, não de `current.day`, e faz `min(day_of_month, último_dia_do_mês_alvo)`.
- Testado em `tests/unit/test_recurrence.py` (5 testes, sem BD): clamp de mês curto, restauro do dia canónico, viragem de ano, anual, e o 29/fev de ano bissexto a cair em 28/fev.

**Decisão — a geração é `POST /recurring-expenses/generate`, invocada à mão (por agora)**: o `ARCHITECTURE.md` (secção 8) diz "invocado por um cron / GitHub Action / APScheduler". Para o âmbito do projeto, um botão "Gerar agora" na UI + uma nota de que em produção seria um job agendado é o MVP honesto — evita mais uma peça de infraestrutura a explicar. O serviço:
- Percorre as recorrências **ativas** com `next_occurrence <= hoje`.
- Para cada uma, faz **catch-up**: enquanto `next_occurrence <= hoje`, cria uma transação datada de `next_occurrence` e avança. Assim, se a app não for aberta durante 3 meses, ao gerar aparecem as 3 rendas em falta, cada uma no seu mês. Cap de `_MAX_CATCH_UP = 120` iterações por recorrência como rede de segurança contra um `next_occurrence` corrompido.
- **Cada transação passa pelo `transaction_service.create_transaction` normal** — a geração não é um caminho especial, os saldos das contas ficam consistentes de graça, e as transações geradas entram automaticamente no dashboard e nos orçamentos (são despesas reais).
- Se a categoria da recorrência tiver mudado de tipo para `INCOME` entretanto (estado inconsistente que o utilizador criou via edição de categorias), a recorrência é **saltada** em silêncio na geração — continua a aparecer como "em atraso" na UI, por isso o utilizador nota.

**Camadas**: `models/recurring_expense.py`, `schemas/recurring_expense.py` (`RecurringExpenseRead` inclui `account_name`/`category_name`/`is_due` resolvidos no service — `is_due = active AND next_occurrence <= hoje`), `repositories/recurring_expense_repository.py` (inclui `list_due_for_user`), `services/recurring_expense_service.py` (a função `advance()` é pública, para o teste unitário), `api/v1/recurring_expenses.py` (`GET`, `POST`, `POST /generate`, `PATCH /{id}`, `DELETE /{id}`).
- FKs RESTRICT novas para `accounts`/`categories` → o `account_service`/`category_service` já apanhavam qualquer `IntegrityError` de FK; só se atualizaram as mensagens de 409 ("...transações **ou despesas recorrentes**...").
- Testes API (`tests/api/test_recurring_expenses.py`, 12 testes): criar, categoria `INCOME` → 422, conta inexistente → 404, gerar cria 1 transação + avança + é idempotente, catch-up de vários meses (`generated == nº de transações`, saldo = inicial − generated×valor), saltar inativas e futuras, editar (valor/ativa/próxima-ocorrência re-deriva `day_of_month`), eliminar, isolamento entre utilizadores, eliminar conta/categoria em uso → 409, exige autenticação. **102 testes no total** (5 unit + 97 API/integração), `ruff` limpo.

**Frontend**: `features/recurring/` (`types.ts`, `api.ts`, `schemas.ts` com zod) + `src/routes/recurring.tsx` (rota `/recorrentes`): cartão "Gerar transações em falta" com contador de recorrências vencidas e feedback ("N transação(ões) gerada(s)" / "Nada a gerar — está tudo em dia"), formulário RHF+zod (descrição, valor, conta, categoria de despesa, frequência, próxima ocorrência, checkbox "Ativa"), e uma lista com badges "Em atraso"/"Pausada", botão rápido Pausar/Retomar, editar inline (mesmo `RecurringForm`) e eliminar com confirmação inline. `generate` invalida `recurring`/`transactions`/`accounts`/`budgets`/`dashboard`. Link "Recorrentes" na navegação do dashboard.

**Validado end-to-end no browser real**: conta Millennium (3000 €), categoria de despesa Habitacao. Criada recorrência "Renda" 550 €/mês com primeira ocorrência 15/06/2026 (hoje = 27/08) → aparece "Em atraso", contador "1 recorrência com ocorrências por lançar". "Gerar agora" → **"3 transação(ões) gerada(s)"**, badge desaparece, próxima ocorrência passa a 2026-09-15. Página de transações mostra as 3 "Renda" (−550 € em 15/06, 15/07, 15/08). Dashboard: saldo global **1350,00 €** (3000 − 3×550), despesas de agosto **550,00 €** (só a de 15/08 conta nesse mês — as outras estão nos seus meses), donut com Habitacao 100%. Utilizador de teste apagado no fim.

---

## 2026-08-27 — Fase 10: Financial Goals (objetivos + projeção de conclusão)

**Objetivo**: registar metas de poupança (fundo de emergência, férias, carro) com valor-alvo, valor já poupado e um prazo opcional, e mostrar quanto é preciso poupar por mês para lá chegar.

**Modelo** (migração `4569675ea483`): `goals` com `name`, `target_amount` (`CHECK > 0`), `current_amount` (`CHECK >= 0`, default 0), `deadline` (nullable). Sem FKs para contas/categorias — um objetivo é uma entidade autónoma (secção 5 do `ARCHITECTURE.md`: `USERS ||--o{ GOALS`). **Sem tabela de histórico de contribuições** — `current_amount` é uma coluna simples que o utilizador ajusta, conforme o `ARCHITECTURE.md` (secção 4).

**Decisão — como muda o `current_amount`**:
- `PATCH /goals/{id}` edita qualquer campo diretamente (nome, alvo, valor, prazo).
- `POST /goals/{id}/contributions {amount}` é o caminho de UX preferido: o utilizador pensa em deltas ("meti 250 este mês"), não em totais. `amount` pode ser negativo para corrigir; o service rejeita (`422`) se o total ficasse < 0.

**Decisão — a projeção é orientada ao prazo, sem depender do histórico de transações**: `GoalRead` traz calculados em runtime: `remaining` (`max(alvo − atual, 0)`), `progress_percentage`, `is_achieved`, e — só quando há prazo futuro e o objetivo não está atingido — `months_until_deadline` (dias até ao prazo / 30, arredondado para cima) e `required_monthly_contribution` (`remaining / meses`, **arredondado para cima** com `ROUND_UP` para que contribuir esse valor chegue mesmo ao alvo). Se o prazo já passou e não foi atingido, `deadline_passed = true`.
- **Porquê não "ao teu ritmo de poupança atinges isto em <data>"**: essa projeção precisaria da poupança mensal média (do dashboard), que é a poupança *total* — dividi-la por vários objetivos não está modelado e daria uma data enganadora se o utilizador tiver 3 metas. A projeção orientada ao prazo é determinística, por-objetivo, e honesta.

**Decisão — PATCH e o prazo nullable**: os outros `*Update` do projeto tratam `None` como "não mexer". Para o prazo isso impediria de o remover depois de definido. O router usa **`"deadline" in payload.model_fields_set`** para distinguir: enviar `{"deadline": null}` limpa o prazo, omitir o campo mantém-no. É a forma correta em Pydantic v2 e vale a pena saber explicar.

**Detalhe — normalização decimal**: quando `current_amount` vem do default Pydantic (`Decimal("0")`) e não de um round-trip à BD, ainda não tem casas fixas — o `_to_read` faz `.quantize("0.01")` a `target`/`current`/`remaining` para a API ser sempre `"0.00"`, não `"0"` (mesmo padrão do dashboard e dos orçamentos).

**Camadas**: `models/goal.py`, `schemas/goal.py`, `repositories/goal_repository.py`, `services/goal_service.py`, `api/v1/goals.py` (`GET`, `POST`, `PATCH /{id}`, `POST /{id}/contributions`, `DELETE /{id}`).
- Testes (`tests/api/test_goals.py`, 14 testes): criar mínimo, alvo ≤ 0 → 422, `required_monthly_contribution` com prazo (900/3 = 300), arredondamento para cima (1000/3 → 333.34), objetivo atingido não tem contribuição exigida, prazo ultrapassado sinalizado, contribuir soma, contribuir até atingir, contribuir para negativo → 422, editar campos, **limpar o prazo com `{"deadline": null}` e mantê-lo ao omitir**, eliminar, isolamento entre utilizadores, exige autenticação. **116 testes no total**, `ruff` limpo.

**Frontend**: `features/goals/` (`types.ts`, `api.ts`, `schemas.ts` zod) + `src/routes/goals.tsx` (rota `/objetivos`): formulário RHF+zod (nome, alvo, já poupado opcional, prazo opcional), e uma lista com barra de progresso (índigo a encher; **verde** quando atingido), nota de prazo contextual ("Poupa €Y/mês nos próximos Z meses (até <data>)" / "Prazo ultrapassado" / "🎉 Objetivo atingido" / "Sem prazo definido"), campo de contribuição inline ("Adicionar"), editar inline e eliminar com confirmação. Link "Objetivos" no dashboard.

**Validado end-to-end no browser real**:
1. "Fundo de emergência" alvo 3000 €, já poupado 500 € → barra a 17%, "Sem prazo definido", "Faltam 2500,00 €".
2. "Ferias" alvo 1200 €, prazo 25/11/2026 (hoje 27/08) → "**Poupa 400,00 €/mês nos próximos 3 meses (até 2026-11-25)**".
3. Contribuir 1200 € para "Ferias" → barra **verde** a 100%, "🎉 Objetivo atingido" (nota de prazo e "Faltam" desaparecem).
4. Editar "Fundo de emergência" a adicionar prazo 27/02/2027 → recalcula: "**Poupa 357,15 €/mês nos próximos 7 meses**" (2500/7, arredondado para cima).

Utilizador de teste apagado no fim.

---

## 2026-08-27 — Fase 11: Monthly History & Analytics (comparação + evolução)

**Objetivo**: navegar entre meses e ver como o mês se compara com o anterior (variação de receitas/despesas/poupança) e a evolução dos últimos meses num gráfico.

**Decisão — módulo `analytics` separado, só leitura, sem tabela**: os dados já existem nas `transactions`; a analytics é agregação por pedido, como o dashboard (Fase 6). Não se estendeu o `dashboard_service` para não o inchar — `analytics_service` reutiliza diretamente o `dashboard_repository.sum_amount_by_type` (que já recebe uma lista de `user_id` e um intervalo de datas).

**Decisão — analytics é sempre da vista individual**: o toggle "Agregado familiar" vive no dashboard (Fase 7). Estender a comparação/evolução ao agregado seria mais superfície de teste sem valor claro para a defesa — fica anotado como iteração futura possível.

**Refactor — `app/core/dates.add_months(day, n)`**: aritmética de meses absolutos (`ano*12 + mês` ± `n`), devolve sempre o dia 1. Usado para "mês anterior" na comparação e para gerar a janela de N meses da evolução. O `month_bounds` foi reescrito em função dele (uma linha). Testes unitários novos em `tests/unit/test_dates.py` (viragem de ano nos dois sentidos, normalização para dia 1).

**Backend**:
- `schemas/analytics.py` — `MonthTotals` (mês + receitas/despesas/poupança), `MonthComparison` (current + previous + `*_change` absolutos + `*_change_pct` — `None` quando o mês anterior foi 0, para não dividir por zero), `MonthlyTrend` (lista de `MonthTotals`, do mais antigo para o mais recente).
- `services/analytics_service.py` — `get_comparison` e `get_trend`. A % de variação é `(atual − anterior) / |anterior| * 100`, arredondada a 1 casa.
- `api/v1/analytics.py` — `GET /analytics/monthly-comparison?month=` e `GET /analytics/monthly-trend?months=6&month=` (`months` validado `2..24` pelo FastAPI → `422` fora do intervalo).
- Testes (`tests/api/test_analytics.py`, 6 testes + 6 unit de datas): deltas e percentagens corretos, sem dados no mês anterior → `pct = None`, série de N meses ordenada e com os meses vazios a `0.00`, `months` fora do intervalo → 422, isolamento entre utilizadores, exige autenticação. **128 testes no total**, `ruff` limpo.

**Frontend**:
- `src/lib/month.ts` ganhou `parseIsoDate` (sem o desvio de fuso de `new Date(string)`) e `shortMonthLabel` ("2026-06-01" → "jun 26", com ano de 2 dígitos porque a série pode cruzar o ano).
- `features/analytics/` (`types.ts`, `api.ts`) + `src/routes/history.tsx` (rota `/historico`): navegação por mês, cartão "Comparação com o mês anterior" com 3 linhas (Receitas/Despesas/Poupança) — cada uma mostra o valor atual e a variação com seta ▲/▼ e **cor que depende da direção "boa"**: receitas/poupança a subir = verde, despesas a subir = vermelho, e vice-versa. Gráfico "Evolução dos últimos 6 meses" = `ComposedChart` do Recharts (barras verdes de receitas + barras vermelhas de despesas + linha índigo de poupança), com `YAxis hide` para o Recharts calcular a escala corretamente com séries mistas barra+linha.
- Link "Histórico" no dashboard.

**Validado end-to-end no browser real** (5 meses de dados, abr–ago 2026):
- Agosto (2200 receitas / 1400 despesas): "Receitas 2200,00 € ▲ 400,00 € (+22.2%)" verde, "Despesas 1400,00 € ▼ 500,00 € (-26.3%)" verde, "Poupança 800,00 € ▲ 900,00 €" verde (mês anterior tinha poupança negativa).
- Recuar para Julho (1800 / 1900): "Receitas ▼ 200,00 € (-10%)" vermelho, "Despesas ▲ 250,00 € (+15.2%)" vermelho, "Poupança -100,00 € ▼ 450,00 €" vermelho.
- Gráfico: barras dimensionadas corretamente, linha de poupança a mergulhar abaixo de zero em julho e a subir em agosto, eixo X com os meses certos, mês sem dados sem barra.

Utilizador de teste apagado no fim.

---

## 2026-08-27 — Fase 12: Insights (motor de regras sobre os dados)

**Objetivo**: transformar os números da app em frases úteis — "o teu orçamento de X está quase esgotado", "gastaste 40% mais do que no mês passado", "este objetivo não vai lá ao ritmo atual".

**Decisão — `GET /insights` é um puro agregador, sem tabela nem lógica de acesso a dados própria**: o `insights_service` não toca no `db` diretamente para queries de domínio — chama os serviços já existentes (`dashboard_service.get_summary`, `analytics_service.get_comparison`, `budget_service.list_budgets`, `goal_service.list_goals`) e aplica regras sobre o que eles devolvem. É o exemplo mais claro do projeto de a arquitetura em camadas a compensar: uma feature nova sem uma linha de SQL nova. Cada insight é `{rule, severity, title, detail}` — `rule` é um id estável (ex: `budget_exceeded`) para a UI dar-lhe um ícone fixo.

**As 8 regras** (todas para o mês pedido, vista individual):
- `budget_exceeded` (aviso) — orçamento acima de 100%.
- `budget_near_limit` (aviso) — orçamento entre 80% e 100%.
- `budget_pace` (aviso) — **só no mês atual**: % do orçamento gasto ultrapassa a % de dias decorridos em mais de 20 pontos (e ainda não está esgotado). É a única regra que precisa de saber "quanto do mês já passou" — daí o parâmetro `today` injetável no service, para os testes.
- `expenses_up` (aviso) / `expenses_down` (positivo) — despesas ≥20% acima / ≥15% abaixo do mês anterior (com um piso de 50 € para não disparar com trocos).
- `negative_net` (aviso) — poupança do mês negativa.
- `healthy_savings` (positivo) — taxa de poupança ≥ 20%.
- `goal_off_pace` (aviso) / `goal_deadline_passed` (aviso) — **só no mês atual**: a contribuição mensal necessária excede a poupança do mês, ou o prazo já passou sem o objetivo estar atingido.
- Ordenadas por severidade: avisos → info → positivos.

**Detalhe — dinheiro nas frases**: o service formata os valores com um helper `_eur` (`"1 400,00 €"`, com espaço não-quebrável, igual ao que o `Intl.NumberFormat('pt-PT')` do frontend produz) — as frases chegam prontas, o frontend não as recompõe.

**Camadas**: `schemas/insight.py`, `services/insights_service.py`, `api/v1/insights.py` (`GET /insights?month=`).
- Testes (`tests/api/test_insights.py`, 13 testes): sem dados → lista vazia, cada regra individualmente (o `budget_pace` via chamada direta ao service com `today=date(2026,8,3)`), ordem avisos-antes-de-positivos, isolamento entre utilizadores, exige autenticação. **141 testes no total**, `ruff` limpo.

**Frontend**: `features/insights/` (`types.ts`, `api.ts`) + cartão **"Alertas do mês"** no dashboard (entre os cartões de estatística e o gráfico), com um ponto colorido por severidade (âmbar `!` / verde `✓` / azul `i`), título e detalhe. Estado vazio: "Sem alertas este mês — está tudo em ordem." Segue o mês selecionado no navegador do dashboard.

**Validado end-to-end no browser real**: utilizador com receita 2500 €/mês, orçamento Casa 200 € (gasto 250 → 125%), orçamento Lazer 100 € (gasto 85 → 85%), despesas do mês (335 €) muito abaixo do mês anterior (1400 €), e um objetivo "Carro" 10 000 € com prazo a 45 dias.
- Mês atual: 5 alertas na ordem certa — 3 avisos (Casa ultrapassado 125%, Lazer quase no limite 85%, "Carro pode não chegar a tempo — precisas de 5 000,00 €/mês e este mês poupaste 2 165,00 €") seguidos de 2 positivos ("Despesas 76% abaixo do mês anterior", "Boa taxa de poupança — 86.6% das receitas").
- Recuar para julho: só 1 alerta ("Gastaste mais do que ganhaste este mês — -1 400,00 €"); os alertas de objetivo desaparecem (só contam no mês atual), e não há alertas de orçamento (os orçamentos são de agosto).

Utilizador de teste apagado no fim.

---

## 2026-08-27 — Fase 13 (parte 1): testes de segurança + endurecimento

**Objetivo**: provar que os riscos clássicos de uma API que mexe em dinheiro estão cobertos — SQL injection, acesso aos dados de outro utilizador, bypass de autenticação, vazamento de segredos — e corrigir o que os testes revelassem.

**Reorganização**: a fixture `client` passou de `tests/api/conftest.py` para `tests/conftest.py` (raiz), ao lado do `db_session`, para ficar disponível também ao novo pacote `tests/security/`. Nenhum teste existente mudou de comportamento.

**`tests/security/test_sql_injection.py` (8 testes)** — o projeto usa sempre o ORM com queries parametrizadas (`select().where(Coluna == valor)`), nunca concatenação de strings SQL. Os testes injetam 9 payloads clássicos (`'; DROP TABLE users; --`, `' OR '1'='1`, `UNION SELECT password_hash ...`, etc.) em **todos** os campos de texto controlados pelo utilizador (nome de categoria/conta/objetivo/agregado, descrição de transação, email de login) e nos parâmetros de query (`type`, `account_id`, `date_from`, `scope`), e verificam: (a) o payload é guardado/devolvido **literalmente** (é dado, não código); (b) o "canário" (uma categoria criada antes) continua lá; (c) nenhum hash bcrypt (`$2b$`) aparece na resposta; (d) tipos fortes nos parâmetros → `422`, nunca execução; (e) depois de uma rajada de tentativas, a app continua 100% funcional (novo registo + login).

**`tests/security/test_authorization.py` (9 testes)** — IDOR consolidado: para **cada** recurso (contas, categorias, transações, orçamentos, objetivos, recorrências, agregados), o utilizador B não vê, não edita e não elimina os objetos de A — mesmo com o id exato — e recebe **`404`, não `403`** (a escolha da secção 8: não confirmar sequer que o id existe). Inclui: B não cria uma transação que referencie a conta/categoria de A; C não aceita nem cancela um convite de agregado dirigido a B.

**`tests/security/test_authentication.py` (8 testes)** — 14 endpoints protegidos exigem token; headers `Authorization` malformados → `401`; token assinado com a chave errada → `401`; **`alg: none`** (token sem assinatura) → `401`; token expirado → `401`; assinatura válida mas `sub` de utilizador inexistente → `401`; assinatura válida mas `sub` não-UUID / em falta → **`401` (não `500`)**.
- **Correção em `app/api/deps.py`**: `uuid.UUID(payload["sub"])` podia levantar `ValueError`/`KeyError` não apanhado → `500` com stack trace. Só um token assinado com a nossa chave chega a esse ponto, mas se a chave vazasse (ou houvesse um bug interno) o modo de falha tem de ser um `401` limpo. Passou a apanhar `(jwt.InvalidTokenError, KeyError, ValueError, TypeError)`.

**`tests/security/test_data_exposure.py` (6 testes)** — `password`/`password_hash` nunca aparecem em nenhuma resposta (verificação recursiva) nem qualquer `$2b$`; o refresh token é guardado **como hash SHA-256** (64 hex), nunca em claro (verificado direto na tabela `refresh_tokens`); o cookie de refresh tem `HttpOnly` + `SameSite=lax` + `Path=/api/v1/auth` + `Max-Age`; o erro de login é **idêntico** para "email não existe" e "password errada" (sem enumeração de contas); um `404` não devolve stack trace nem menciona `sqlalchemy`.

**`tests/security/test_input_hardening.py` (6 testes)** — valores que a BD rejeitaria são apanhados com `422` antes do insert, nunca `500`:
- **Endurecimento nos schemas**: `Field(max_digits=12, decimal_places=2)` em todos os campos monetários (conta, transação, orçamento, objetivo, contribuição, recorrência) — `NUMERIC(12,2)` overflow ou 3 casas decimais → `422`. `max_length` nos campos de texto que não o tinham (nome de categoria/conta = 100, descrição de transação = 200, `icon`/`color`) — strings gigantes → `422`.
- Montantes ≤ 0 em campos `gt=0` → `422`. **Mass-assignment**: campos extra no corpo (`user_id`, `id`, `current_balance`) são ignorados pelo Pydantic — a conta criada é do autor, com id gerado pelo servidor e `current_balance == initial_balance`. JSON malformado → `422`.

**Resultado**: **178 testes a passar** (141 → 178), `ruff` limpo. Smoke test contra o servidor a correr (registo/login/dashboard OK; overflow → 422; token inválido → 401) e verificação visual no browser de que o dashboard continua a funcionar depois do endurecimento. Nenhuma alteração ao frontend (as validações de comprimento no cliente ficam para o polish da Fase 16).

**Gaps de segurança assumidos (fora do âmbito do projeto, a mencionar na defesa se perguntado)**: sem rate limiting / proteção de força bruta no login; sem CSRF token explícito (mitigado por `SameSite=lax` + o access token ir no header `Authorization`, não num cookie); sem cabeçalhos de segurança HTTP (HSTS, CSP) — esses são responsabilidade da camada de deployment (Fase 15).

---

## 2026-08-27 — Fase 13 (parte 2): endurecimento, CI, e testes de casos-limite

Revisão transversal do projeto (segurança, funcionamento, Docker, CI). O que se corrigiu/melhorou:

**Autenticação — deteção de reutilização de refresh token (resposta a roubo)**: antes, apresentar um refresh token já rodado dava só um `401`. Agora, se o token existe mas está revogado, assume-se roubo e **revoga-se toda a família de tokens do utilizador** (`refresh_token_repository.revoke_all_for_user`), obrigando a novo login em todo o lado — nem o token legítimo mais recente sobrevive. O router de `/refresh` passou a fazer `db.commit()` também no caminho de erro, para a revogação em massa ficar persistida. Teste novo em `test_auth.py`; confirmado também com um smoke test contra o servidor a correr.

**Config — `SECRET_KEY` à prova de erro**: `config.py` ganhou validadores Pydantic — a chave tem de ter ≥ 32 caracteres (RFC 7518) em qualquer ambiente, e fora de `development` a app recusa-se a arrancar se a chave contiver marcadores de placeholder (`change`, `example`, `placeholder`, …). Propriedade `settings.is_production` (`environment` não é `development`/`dev`/`local`/`test`). O `.env.example` passou a ter um `SECRET_KEY` que funciona em dev mas falha em produção, e o README explica como gerar um real. 5 testes unitários em `tests/unit/test_config.py`.

**Robustez de ligação à BD**: `create_engine(..., pool_pre_ping=True)` — cada ligação do pool é testada antes de ser usada, para não rebentar com "connection already closed" se o Postgres reiniciar (ex: `docker compose restart postgres`).

**Docker**:
- `.dockerignore` no `backend/` e no `frontend/` — o contexto de build deixou de enviar `node_modules`/`.venv`/`.env`/`dist`/`.git`. No frontend isto elimina um risco real: o `COPY . .` do Dockerfile trazia o `node_modules` do host (Windows) para dentro da imagem Linux, por cima do `npm ci`.
- Healthcheck no serviço `backend` do `docker-compose.yml` (faz `GET /health` a cada 10s), e o `frontend` passou a `depends_on: backend: condition: service_healthy` — `docker compose up` só dá o frontend por pronto depois de a API responder. Validado: `backend running healthy`.

**CI — `.github/workflows/ci.yml` cresceu de 2 para 6 jobs** (era "Fase 0: só lint"): `lint-backend`, `lint-frontend`, **`test-backend`** (com `services: postgres` real, `alembic upgrade head`, `pytest`), **`build-frontend`** (`tsc + vite build`), **`build-images`** (`docker build` dos dois Dockerfiles, para os validar). É essencialmente a Fase 14 adiantada. Os dois `docker build` foram testados localmente e passam.

**Testes de casos-limite (`tests/api/test_edge_cases.py`, 6 testes)**: eliminar a conta que é *destino* de uma transferência → `409` (a FK `destination_account_id` também é RESTRICT, não só `account_id`); transação num mês muito no futuro (2030-12) não conta no mês atual mas conta em dezembro/2030 e já move o saldo global (aritmética de mês na fronteira do ano); converter uma transação `EXPENSE` → `TRANSFER` limpa a categoria e reaplica os saldos corretamente; transferência sem conta de destino → `422`; último membro a sair de um agregado leva os convites pendentes em cascata; o parâmetro `month` do dashboard aceita qualquer dia do mês.

**Resultado**: **190 testes a passar** (178 → 190), `ruff` limpo, `docker compose config` válido, os dois `docker build` a passar, backend `healthy`.

### Melhorias identificadas e ainda por fazer (backlog priorizado)

| Prioridade | Item | Onde |
|---|---|---|
| Alta | Suite Playwright E2E (4–6 fluxos) — é a parte que falta da Fase 13 | `frontend/e2e/` |
| Alta | Rate limiting no `/login` e `/register` (ex: `slowapi`) — mitiga força bruta | `app/main.py` |
| Média | Limpeza periódica de `refresh_tokens` expirados/revogados (a tabela cresce sempre) — endpoint de manutenção ou job | `app/services/auth_service.py` |
| Média | Logging estruturado de erros (requisito não-funcional da secção 3 do `ARCHITECTURE.md`, ainda por implementar) | `app/core/` |
| Média | React error boundary — hoje um erro num componente de rota deixa a app em branco | `frontend/src/` |
| Média | Dockerfiles de **produção** (frontend: `vite build` + nginx; backend: sem `--reload`, sem `uv`) — Fase 15 | `*/Dockerfile.prod` |
| Baixa | `maxLength` nos inputs do frontend a espelhar os limites novos dos schemas — Fase 16 (polish) | `frontend/src/routes/` |
| Baixa | Desativar `/docs` (Swagger) fora de `development` | `app/main.py` |
| Baixa | Code-splitting por rota (bundle ~850 kB por causa do Recharts) — Fase 16 | `frontend/vite.config.ts` |
| Baixa | Cabeçalhos de segurança HTTP (HSTS, CSP, X-Content-Type-Options) — camada de deployment, Fase 15 | reverse proxy / `app/main.py` |
| Baixa | Mudar o `sub` do JWT para incluir `type` e validar `payload["type"] == "access"` no `deps.py` (defesa extra contra confundir access/refresh — hoje o refresh nem é JWT, por isso o risco é teórico) | `app/api/deps.py` |
