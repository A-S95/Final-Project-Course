# CentiSible — Diário de Desenvolvimento

> Nota: o projeto chamou-se "FinTrack" até 2026-08-29, quando o rebatizei para "CentiSible" — ver a entrada datada dessa mudança. As entradas anteriores a essa data usam o nome antigo de propósito (registo histórico do que era verdade na altura), não corrijo isso.

> Registo do meu processo mental enquanto construo isto: decisões, alternativas que considerei, problemas que encontrei e como os resolvi. Serve de apoio à minha apresentação/defesa do projeto — cada entrada explica o "porquê", não só o "o quê" (isso já está no código e no `ARCHITECTURE.md`).

---

## Estado atual (ler isto primeiro ao retomar o projeto)

*Atualizado em: 2026-08-30*

**Resumo de 30 segundos para retomar amanhã**: **A app está online a sério e já emprestei a dez amigos para testarem.** O backend está na Render (`centisible.onrender.com`), a base de dados na Neon, e o frontend na Vercel (`centisible.vercel.app`). Pelo caminho apanhei um bug real: a sessão morria logo a seguir ao login em produção, porque o cookie do refresh token tinha `samesite="lax"`, que os browsers nunca enviam entre domínios diferentes (corrigido, ver entrada "Bug real: a sessão morria..."). Escolhi a hospedagem depois de a Fly.io se revelar paga (ver entrada "Escolhi onde alojar a sério"), e tive de corrigir dois problemas de configuração na Render antes do primeiro deploy limpo (ver as duas entradas sobre isso). Reescrevi o texto da landing page para soar mais humano e menos genérico, e acrescentei animações novas. Criei dez contas de teste (`teste1@teste.com` a `teste10@teste.com`, password `Teste1234`) com dois anos de dados cada, já a viver na Neon, prontas a dar aos amigos. Instalei a app no meu telemóvel Android a sério e confirmei que funciona. **Dei uma limpeza a este diário** — estava a escrever como se fosse outra pessoa a pedir-me coisas, agora lê-se como eu próprio a contar o que fiz. **Transformei isto numa PWA** (manifest, ícones, service worker) — instalação testada e confirmada no Chrome e no Edge do PC. Ver entrada de hoje "PWA: manifest, ícones e service worker". **Deploy e instalação no telemóvel, já feitos** — ver as entradas de hoje sobre a escolha de alojamento, a Render e o bug do cookie. **Fiz uma varredura ao código todo** (backend e frontend): sem erros reais, um caso de código morto removido (`subscribeAccessToken`, nunca usado), e comentários de bloco cortados para uma linha em 53 ficheiros. Corrigi também o retângulo preto feio ao tocar num gráfico em mobile (faltava desligar o realce de toque por omissão do Recharts). **Em aberto para a próxima sessão, se continuar**: lista completa em `ARCHITECTURE.md`, secção "Pontos em aberto" — o mais importante de tudo é que as despesas recorrentes não se geram sozinhas (só com um clique manual), o resto é recuperação de password/confirmação por email, cabeçalhos de segurança, scan de dependências no CI, exportar dados, notificações push, e a questão dos recibos sem disco persistente na Render. **Mudei a identidade visual da app — de violeta/teal para "Oliva" (verde profundo + âmbar raro)**, escolhida entre três opções que pré-visualizei antes de decidir. Apliquei a sério em `index.css` (tokens `--accent`/`--accent-strong`/`--accent-soft`, mais `--accent-teal` renomeado para `--accent-amber`) — propaga-se sozinho a toda a app via Tailwind. Redesenhei o logótipo para a nova paleta (C verde, moeda âmbar). Ver entrada "Nova paleta de marca: Oliva". **Dei aos cartões pré-pagos abaixo do plafond (ex: Universo) um botão "Recarregar plafond"** que abre Transações já com o formulário de criação preenchido (conta, tipo, valor em falta) — apanhei pelo caminho um bug real de navegação (`navigate()` dentro de um `useEffect`, a interagir mal com o `AnimatePresence` do `ProtectedRoute`, fechava o formulário sozinho um instante depois de abrir). Ver entrada "Recarregar plafond nos cartões pré-pagos". **Reordenei o painel principal em mobile** — Insights e Próximos pagamentos (urgente) sobem para logo a seguir aos cartões de saldo; Despesas por categoria e Objetivos (para explorar com calma) passam a um separador simples mais abaixo, em vez de mais scroll. Desktop inalterado. Ver entrada "Painel principal: ordem diferente em mobile". **Fechei o logótipo definitivo da marca** — um "C" com um gráfico de crescimento e uma moeda desenhados dentro (baseado num style guide que tinha, `logotipostyle.png`), a substituir a moeda genérica de antes, em todos os sítios onde a marca aparece (sidebar, splash, landing, login, registo, favicon). Ver entrada "Logótipo definitivo: o C com o gráfico dentro". **Fiz a lista de Transações agrupar por dia (Hoje/Ontem/...), clicar numa transação abre um MODAL de detalhe (conta, categoria, data, recibo) — não um painel embutido na página (esse tinha um bug real em mobile: abria no topo, fora do scroll atual) —, e dá para anexar um recibo (foto/PDF) a uma transação** — guardado em disco num volume novo (`uploads_data`), servido só ao dono via endpoint autenticado, nunca por URL pública. **python-multipart é a primeira dependência nova do projeto**. Ver entrada "Transações agrupadas por dia, painel de detalhe e recibos anexados". **Rebatizei o projeto para "CentiSible"** (era "FinTrack", mudei em 2026-08-29, com logo novo — uma moeda com "¢" — animado onde faz sentido; ver entrada "Rebatizado para CentiSible"). Dei ao painel principal "CentiSible Insights" (renomeado de "Alertas do mês") e um cartão "Próximos pagamentos" com crachás de marca genéricos (sem logótipos reais, só ícone+cor por questão de direitos de autor), layout 2×2 simétrico inspirado num mockup que tinha (`exemplo.png`), e resolvi a navegação entre páginas a "piscar" — a sidebar já não remonta a cada clique (rota de layout do React Router) e o React Query mantém os dados antigos visíveis durante um refetch (`keepPreviousData`) em vez de esvaziar o ecrã (ver entrada "CentiSible Insights, Próximos pagamentos e navegação sem piscar"). Backend tudo feito e a passar, **CI incluído — os 6 jobs do GitHub Actions estão todos verdes** (ver entrada "Primeira corrida real do CI"). Fiz uma ronda grande de trabalho no frontend ("elegante, chamativo, boas animações" era o objetivo) — navegação lateral persistente, números animados, layout a duas colunas nas páginas de lista, um bug real de flexbox (`mx-auto` sem `w-full` fazia o `max-w` nunca ter efeito), Objetivos no painel, cards de saldo por conta no painel + validade/plafond de cartões com alertas em Insights, e (o mais importante fora de UI) **um bug de correção de dados**: a fusão de "Despesas por categoria" no agregado familiar fundia por nome cegamente — corrigi para só fundir despesas de facto marcadas `is_shared`, mantendo despesas pessoais homónimas separadas por pessoa (`owner_name`). Ver a sequência de entradas de hoje, mais recente no topo de cada bloco. **Repus as contas de demonstração do zero** com um ano de dados novo, incluindo renda partilhada com valores diferentes por pessoa (500€/300€) para provar que a fusão soma correto independentemente da divisão; a conta "Universo" tem agora plafond 1000€ + validade próxima para demonstrar o novo alerta. **Ainda por fazer, se eu continuar**: landing/login não foram revistas nesta ronda de frontend. 231 testes backend + 9 E2E a passar. A app está a correr agora (`docker compose up -d` já ativo — 3 containers `healthy`, imagens do frontend e do backend reconstruídas para o `index.html` novo e o `python-multipart` refletirem).

**Fase em curso**: **Roadmap principal (Fases 0–16) concluído**, mais adições ao longo de várias sessões (contas de demonstração, despesas partilhadas, reformulação visual partes 1+2, rate limiting/logging/cleanup, seletor de ícone/cor de categoria, CI validado, revamp geral do frontend interno, correção da fusão de despesas do agregado) — ver entradas datadas abaixo. `ruff`/`oxlint`/`build` limpos.

**Contas de demonstração — não apagar sem pensar duas vezes**: `antonio@teste.com` e `teresa@teste.com` (password `Teste1234`) têm ~12 meses de dados reais gerados por script (não commitado ao repo, ficou só num scratchpad local). **Repus do zero em 2026-08-29** (ver entrada de hoje "Reset das contas de demonstração") — conta "Conta Principal" cada, 8 categorias com ícone/cor, ordenado de 1200€/mês, renda partilhada com **valores diferentes por pessoa de propósito** (Antonio 500€, Teresa 300€ — fundem-se em 800€ na vista de agregado), um objetivo cada, uma recorrência (Netflix, Antonio) e um orçamento cada no mês atual. Ao contrário de todas as outras contas de teste usadas neste diário, **estas ficam persistidas de propósito** para eu testar a app manualmente — nunca apagar com o `DELETE FROM users WHERE email LIKE '%@example.com'` de limpeza habitual (esse padrão não as apanha, mas cuidado ao escrever queries de limpeza novas).

**Efeito colateral disto num teste de segurança**: `tests/security/test_data_exposure.py::test_refresh_token_is_stored_hashed_not_in_plaintext` assume a tabela `refresh_tokens` vazia antes de correr (conta `len(stored) == 1` depois de UM registo). Como as contas de demonstração (e qualquer sessão manual de login) deixam sempre tokens na tabela, este teste específico falha sempre que eu testar a app manualmente antes de correr `pytest`. **Não é um bug** — corrijo com `docker exec projetofinal-postgres-1 psql -U fintrack -d fintrack -c "TRUNCATE refresh_tokens;"` antes de correr a suite (não apaga utilizadores nem dados financeiros, só sessões).

**Sessão de 2026-08-27 (a maior até agora)**: implementei de raiz as Fases **6 (Dashboard v1)**, **7 (Households)**, **8 (Budgets)**, **9 (Recurring Expenses)**, **10 (Financial Goals)**, **11 (History & Analytics)**, **12 (Insights)** e a **Fase 13 (parte 1 e 2)**. Cada uma tem a sua entrada datada abaixo, com o "porquê" das decisões e a validação visual no browser.

**Ambiente desta máquina** (tudo instalado e a funcionar — não preciso de repetir nada):
- Node/npm, Python 3.12.10, uv 0.12.5, Docker Desktop 4.87.0 + WSL2.
- Backend: `cd backend && uv run pytest` → **209 testes a passar** (ver nota acima sobre `refresh_tokens`); `uv run ruff check .` limpo. Precisa do Postgres do `docker-compose` a correr.
- Frontend: `cd frontend && npm run build` + `npm run lint` — limpos. **Playwright instalado** (`@playwright/test` + browser Chromium via `npx playwright install chromium --with-deps`) — `npm run test:e2e` corre a suite de **9** testes (precisa do `docker compose up -d` a correr, app em `:5173`/API em `:8000`). `playwright.config.ts` corre com `reducedMotion: 'reduce'` — ver entrada de hoje sobre porquê.
- Dashboard agora está em `/dashboard`, não em `/` (mudei nesta sessão — `/` é a landing page pública).
- Tema claro/escuro tem alternador manual (botão sol/lua no canto superior direito de todas as páginas), persistido em `localStorage` (`centisible-theme`) — antes desta sessão só seguia o SO, sem opção manual.
- `docker compose up -d` sobe `postgres` + `backend` (com healthcheck) + `frontend`; app em `http://localhost:5173`, API em `http://localhost:8000` (`/docs` para o Swagger).
- **Stack de produção** (`docker-compose.prod.yml`) construída e validada manualmente numa sessão anterior. Ver `README.md` (secção "Deployment").
- **Correções de ambiente já embutidas** (não repetir): Vite com `usePolling: true` no Docker Windows (Fase 3); `bcrypt` chamado diretamente em vez de `passlib` (Fase 2); `join_transaction_mode="create_savepoint"` nos testes (Fase 2).

**Base de dados**: 11 tabelas, migrações Alembic até `6a85071ceaea` (`add receipt_content_type to transactions`). Tabelas: `users`, `refresh_tokens`, `accounts`, `categories`, `transactions`, `households`, `household_members`, `household_invites`, `budgets`, `recurring_expenses`, `goals`.

**Dependências novas nesta ronda**: nenhuma — a reformulação visual usa o `motion` que já estava instalado desde a Fase 0 mas que nunca tinha usado (0 animações na app antes desta sessão).

**Git/GitHub**: giro isto sempre eu, manualmente, sem scripts nem automação — init, commits, branches, push, PRs, Actions. A pasta **ainda não é um repositório git** nalgumas destas entradas mais antigas (`git init` por fazer nessa altura).

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
2. ~~Validar em CI real~~ — **feito e confirmado nesta sessão, ver entrada "Primeira corrida real do CI" abaixo**: apanhei 4 bugs latentes, todos corrigidos; os 6 jobs do `ci.yml` estão verdes. Ainda por considerar (opcional, não é preciso): um job que construa as imagens `Dockerfile.prod` (a `build-images` atual só constrói as de desenvolvimento).
3. ~~Seletor de `Category.icon`/`color` e reatribuir transações a outra categoria antes de eliminar~~ — **feito, ver entrada de hoje "Seletor de ícone/cor de categoria e reatribuição de transações ao eliminar" abaixo**.

**Nova funcionalidade planeada — Households (agregado familiar)**: adicionei ao roadmap como Fase 7 (a seguir ao Dashboard v1). Ver `ARCHITECTURE.md` secções 2, 4, 5 e 8 para o desenho completo.

**Onde está tudo**: projeto em `C:\Users\anton\Desktop\Projeto final\` — `backend/` (FastAPI), `frontend/` (React/Vite), `docs/ARCHITECTURE.md` (arquitetura/ERD/roadmap), este ficheiro (`docs/DEV_JOURNAL.md`, decisões e histórico).

---

## 2026-08-30 — Varredura ao código todo, e um levantamento do que falta

Antes de fechar a sessão, pedi uma revisão geral ao projeto inteiro: erros, código morto, e reduzir os comentários (o código tinha acumulado muitos comentários de parágrafo, úteis durante o desenvolvimento mas a mais para ficar no repositório final). Corri isto em duas frentes ao mesmo tempo, backend e frontend.

Backend: sem código morto nem erros reais. Cortei os comentários de bloco de 29 ficheiros para uma linha cada, mantendo só o "porquê" que não é óbvio pelo próprio código (o `SameSite` a mudar em produção, o `RESTRICT` em vez de `CASCADE`, a lógica de fusão de despesas partilhadas). `ruff` limpo, 231 testes a passar depois.

Frontend: encontrei um caso real de código morto, `subscribeAccessToken` em `api/token-store.ts` (um mecanismo de subscrição inteiro que nunca chegou a ser usado, o `AuthContext` geria o estado de outra forma). Removi. Cortei comentários em 24 ficheiros, mesmo critério do backend. `lint`/`build` continuam limpos.

Fechei também um bug de UI real: no telemóvel, tocar num gráfico (o círculo do dashboard, o de barras do histórico) deixava um retângulo preto feio à volta do elemento tocado. Não era a tooltip, essa já estava bem estilizada, era o próprio elemento SVG do Recharts sem nada a desligar o realce de toque por omissão do browser. Corrigi com `-webkit-tap-highlight-color: transparent` e `outline: none` nos elementos do `.recharts-wrapper`, em `index.css`.

Por fim, fui à procura de mais coisas a rever a sério, não só perguntar "o que falta" de memória. Encontrei uma real: as despesas recorrentes não se geram sozinhas, só quando alguém carrega manualmente no botão "Gerar transações em falta". Também reparei que a limpeza de `refresh_tokens` (a cada 24h, dentro do próprio processo) raramente completa um ciclo inteiro na Render grátis, que adormece ao fim de 15 minutos parada. Juntei estas duas mais as ideias de segurança/funcionalidade que discuti (recuperação de password, confirmação por email, cabeçalhos de segurança, scan de dependências, 2FA, exportar dados, notificações push, importar extrato) na secção "Pontos em aberto" do `ARCHITECTURE.md`, para retomar quando continuar.

---

## 2026-08-30 — Dez contas de teste, com dois anos de dados cada, para os amigos experimentarem

Para os amigos poderem experimentar a app a sério, sem terem de criar uma conta vazia e preencher tudo à mão, escrevi um script (`backend/scripts/seed_friend_accounts.py`, fora do controlo de versões, tal como o script das contas de demonstração locais) que cria contas `teste1@teste.com` a `teste10@teste.com` (password `Teste1234` para todas), cada uma com uma conta bancária, oito categorias, orçamentos do mês, um objetivo com progresso parcial, uma despesa recorrente e quase 400 transações espalhadas por 24 meses.

Testei primeiro contra a base de dados local, com só duas contas, para apanhar qualquer erro sem arriscar a Neon. Confirmei os números por SQL direto e fiz login a sério pela API local antes de avançar. Depois de limpar essas duas contas de teste locais, corri o script a sério contra a Neon, para as dez contas pedidas.

Confirmei tudo pelo site verdadeiro, com a `teste5`: o painel carregou com saldo, gráfico de despesas por categoria e até um alerta genuíno de orçamento ultrapassado, que surgiu naturalmente dos dados aleatórios gerados. Não forcei nada, foi mesmo o motor de insights a fazer o trabalho dele.

---

## 2026-08-30 — Confirmei tudo em produção depois do commit, e instalei no telemóvel a sério

Depois do commit e push, fui às duas plataformas confirmar que o deploy automático tinha apanhado a versão nova. Ambas confirmaram, a Render com o "Auto-Deploy" a correr sozinho a partir do push, a Vercel também. Ao ir testar no browser, a primeira vez que abri o site ainda me apareceu o texto antigo da landing page. Era só cache do próprio browser, um recarregar forçado (Ctrl+Shift+R) resolveu.

Testei o login a sério desta vez, com sessão nova: entrei, o dashboard carregou por completo sem nenhum 401, e confirmei que a sessão sobrevive a um recarregar da página inteira. Isso prova que a correção do cookie realmente resolveu o problema em produção, não só localmente.

Por fim, instalei a app no meu telemóvel Android. O Chrome não mostrou o banner automático de instalação, só a opção manual no menu de hambúrguer ("Instalar app"). Confirmei que isto é normal, o banner automático depende de heurísticas de utilização do Chrome que nem sempre disparam, e o resultado final é idêntico: o ícone fica no ecrã principal e a app abre em modo standalone.

---

## 2026-08-30 — Landing page: texto mais humano e umas animações a mais

Antes de fazer o commit de tudo isto, revi a landing page: gostava da apresentação visual, mas o texto lia-se a "modelo de SaaS genérico", e queria mais animação para ficar mais chamativa.

Reescrevi o texto de quase todas as secções (hero, funcionalidades, agregado familiar, chamada final, rodapé) a trocar frases de especificação técnica por linguagem mais próxima de uma pessoa real a explicar o problema que resolve. Por exemplo, troquei "sem folhas de cálculo e sem surpresas no fim do mês" por "sem abrir uma folha de cálculo às 23h a tentar perceber para onde foi o dinheiro". Numa primeira ronda ainda usei travessões a mais para ligar ideias, um tique que se nota facilmente como texto escrito por IA. Numa segunda ronda tirei esses travessões todos e reescrevi essas frases como duas frases curtas, ou com "mas"/"e" a ligar as ideias em vez de as colar com um travessão.

Também acrescentei animações novas: o saldo do cartão da hero agora conta a subir do zero (reaproveitei o `AnimatedNumber` que já uso no dashboard a sério), um brilho suave a flutuar atrás desse cartão, um brilho lento e contínuo no gradiente de "à vista.", os cartões de funcionalidades a levantarem-se com um brilho na borda ao passar o rato, uma seta que desliza nos botões principais, e a seta "↓" da secção do agregado a pulsar suavemente. Tudo desligado automaticamente para quem tiver "reduzir movimento" ativo no sistema, o mesmo padrão já usado no resto da app.

---

## 2026-08-30 — Bug real: a sessão morria logo a seguir ao login em produção

Depois de tudo isto no ar, testei a sério: registei uma conta de teste no site já em produção. O registo funcionou, o login também, mas assim que a app tentava carregar o dashboard, tudo vinha com 401, incluindo o pedido de renovação automática da sessão. A app entrava num ciclo sem fim: pedir dados, falhar, tentar renovar, falhar outra vez.

Fui direto ao código do cookie do refresh token e encontrei a causa: estava marcado `samesite="lax"`. Um cookie "lax" nunca é enviado pelo browser em pedidos entre sites diferentes, só entre portas diferentes do mesmo site. Em dev local isto nunca aparecia porque o frontend e o backend só diferem na porta (`localhost:5173` e `localhost:8000`, o mesmo site). Em produção, o frontend está na Vercel e o backend na Render, dois domínios completamente diferentes, por isso o cookie nunca chegava a ser enviado de volta.

Corrigi para `samesite="none" if settings.is_production else "lax"` (o "none" exige `Secure`, que já estava ligado só em produção, por isso as duas condições andam a par). Antes de dar como resolvido, corri os 47 testes relacionados com autenticação e cookies mais o `ruff`, tudo limpo. O teste que confirma as flags do cookie continua a esperar "lax", porque corre com `ENVIRONMENT=test`, não `production`, por isso não precisou de mudar.

---

## 2026-08-30 — Na Vercel, ao contrário da Render, dá para mudar de domínio a sério

O frontend na Vercel também tinha ficado com o nome do repositório, `final-project-course`, e o domínio `final-project-course-sigma.vercel.app`. Desta vez correu melhor: mudei o nome do projeto para `centisible` nas definições e depois fui a Domains e simplesmente pedi `centisible.vercel.app` como domínio novo. Ficou disponível de imediato, sem ter de apagar nada. O domínio antigo continua ativo como alias, não faz mal nenhum deixá-lo.

Atualizei o `CORS_ORIGINS` na Render para incluir os dois domínios da Vercel, para não haver surpresas se alguém ainda tiver o link antigo guardado.

---

## 2026-08-30 — Recriei o serviço da Render só para ter um URL apresentável

O nome que a Render deu ao serviço por omissão veio do nome do repositório, `final-project-course`, e o domínio ficou `final-project-course-zppf.onrender.com`. Como isto vai para o CV, queria algo com o nome da marca. Mudei o campo "Name" nas definições para "Centisible", mas o domínio `.onrender.com` não mudou. Fui às definições de domínio à procura de um campo para editar isso e não há: só existe um interruptor para ativar ou desativar o subdomínio da Render, sem forma de o renomear depois de criado.

A única forma de ter um domínio limpo era apagar e recriar o serviço com o nome certo desde o início. Apaguei o serviço antigo (a base de dados na Neon não foi afetada, é um recurso à parte) e criei um novo já chamado `centisible`, desta vez a acertar o `Dockerfile Path` logo no formulário de criação, para não repetir o mesmo erro de antes. Também tive de gerar uma `SECRET_KEY` nova, porque a antiga nunca me tinha sido mostrada (fica sempre mascarada no painel da Render). O domínio ficou `centisible.onrender.com`, e o deploy correu bem à primeira desta vez, com uma pequena pausa a meio em que a Render detetou a porta 8000 e reiniciou o deploy sozinha para atualizar a configuração de rede. É normal na primeira vez que um serviço arranca.

---

## 2026-08-30 — O primeiro deploy da Render não correu bem à primeira

Criei a base de dados na Neon sem problemas (projeto `centisible`, região Frankfurt, perto de Portugal). Depois criei o serviço na Render, ligado ao mesmo repositório do GitHub, com o "Root Directory" a apontar para `backend`.

O primeiro deploy falhou com `ModuleNotFoundError: No module named 'psycopg2'`. A causa era simples: tinha colado a connection string da Neon tal como ela vem, `postgresql://...`, e sem o `+psycopg` a apontar para o driver certo, o SQLAlchemy tenta usar por omissão o `psycopg2`, que não está instalado neste projeto (uso o `psycopg` v3). Corrigi a variável para `postgresql+psycopg://...` e voltei a tentar.

O segundo deploy pareceu correr bem, mas ao ver os logs com atenção, algo estava errado: o arranque mostrava um `uvicorn --reload` que eu nunca configurei, e não havia rasto nenhum das migrações do Alembic a correr. A build também não batia certo com o `Dockerfile.prod` real, tinha menos passos do que devia, sem a fase de build a duas etapas que tenho. A causa era o campo "Dockerfile Path", que tinha ficado no valor por omissão (`Dockerfile`). Como não existe nenhum ficheiro com esse nome em `backend/`, a Render caiu silenciosamente para a deteção automática dela própria, em vez de avisar que não encontrou o ficheiro certo.

Corrigi o caminho para `backend/Dockerfile.prod` e o deploy seguinte já correu como devia: as onze migrações do Alembic todas aplicadas, o Uvicorn a arrancar limpo, sem `--reload`, e o healthcheck a passar. Confirmei de fora com um `curl` ao `/health` e recebi `{"status":"ok","environment":"production"}`.

---

## 2026-08-30 — Escolhi onde alojar a sério: a Fly.io ficou pelo caminho, fui para Render + Vercel + Neon

Depois de decidir ontem que a PWA vinha primeiro, hoje foi a vez de escolher onde pôr isto a correr a sério. Comecei pela Fly.io, que tinha em mente da pesquisa anterior. A instalação da CLI deu erro no meu PowerShell (era só a PATH da sessão que ainda não tinha atualizado, resolveu-se ao abrir uma janela nova). Depois de autenticar, tentei criar a app com `fly launch`, mas isso foi bloqueado automaticamente, porque provisiona recursos reais numa conta minha e tem de pedir confirmação primeiro.

Entretanto fui eu próprio ver o site da Fly.io e encontrei um formulário de criação pela interface, ligado ao GitHub. Antes de avançar, confirmei os preços atuais em vez de confiar em memória, e ainda bem que o fiz: a Fly.io deixou o plano gratuito em 2024, e o "Managed Postgres" que o formulário sugeria custa a partir de 38 dólares por mês. Por cima disso, aquele formulário também não encontrava o `Dockerfile.prod` (só procura um ficheiro chamado `Dockerfile`, sem opção para indicar outro nome).

Como o objetivo era mesmo grátis e sem complicações, mudei de plano: a Render para o backend, a Neon para o Postgres e a Vercel para o frontend. Confirmei os três antes de avançar. A Render tem plano grátis sem cartão de crédito, a Neon tem um tier permanente e generoso, e a Vercel encaixa bem com um build Vite simples. Nada disto exigiu cartão de crédito em lado nenhum.

---

## 2026-08-30 — PWA: manifest, ícones e service worker

Segui o plano da entrada anterior de hoje: PWA primeiro, porque não depende de decidir onde alojar. Usei o `vite-plugin-pwa` (gera o manifest e o service worker a partir de config no `vite.config.ts`, em vez de escrever isso à mão) — primeira dependência nova desde o `python-multipart`.

**Ícones**: a marca já estava pronta (o "C com o gráfico e a moeda" do `favicon.svg`), só faltava gerar os tamanhos que uma PWA exige — 192×192 e 512×512 normais, mais uma versão "maskable" (a marca ocupa só ~55% do canvas, com fundo branco sólido, para sobreviver ao recorte em círculo/squircle que o Android aplica) e um `apple-touch-icon` (também fundo sólido — o iOS lida mal com PNGs transparentes, mete-lhes fundo preto). Não tinha nenhuma ferramenta de conversão SVG→PNG instalada nesta máquina (sem ImageMagick/Inkscape), por isso instalei o `sharp` com `--no-save` só para correr um script (`frontend/scripts/generate-pwa-icons.mjs`, fica no repo para se a marca voltar a mudar) e não entrou no `package.json` — é uma ferramenta de um só uso, não uma dependência da app.

**Decisão sobre cache da API**: como isto é uma app de finanças, era importante que o service worker nunca mostrasse saldos ou transações desatualizados a fazer-se passar por dados reais. Por omissão o `generateSW` só faz precache dos ficheiros do build (JS/CSS/ícones) e nem sequer intercetava os pedidos à API (API noutra origem — porta diferente em dev, domínio diferente em produção). Mesmo assim, tornei isso explícito com uma regra `runtimeCaching` a apanhar tudo o que bate em `/api/` e a forçar `NetworkOnly` — não é preciso confiar num comportamento por omissão implícito, fica escrito e é fácil de explicar na defesa.

**`theme-color` estava desatualizado**: o `index.html` ainda tinha `#08090d` no `<meta name="theme-color">`, de antes da mudança de paleta para "Oliva" — corrigi para `#1f7a4c` (o verde de marca), que é também o `theme_color` do manifest agora.

**Testado e confirmado**: `npm run build` gera `sw.js` + `manifest.webmanifest` corretamente injetados no `<head>`; corri `vite preview` e confirmei no browser (com o Chrome MCP a validar por script: service worker `activated`, manifest a servir com `content-type: application/manifest+json`, ícones todos a responder 200) que os critérios de instalabilidade estavam todos cumpridos. Depois testei a instalação a sério — funcionou tanto no Chrome como no Edge do PC. **Falta só testar num telemóvel**, mas isso exige HTTPS público (um service worker não regista fora de `localhost` ou HTTPS), por isso fica para depois do deploy.

---

## 2026-08-30 — Devia isto ser uma app? (pesquisa, ainda por decidir)

Aproveitei para dar uma limpeza a este diário — ao reler as entradas percebi que estava a escrever como se estivesse a documentar pedidos de outra pessoa ("o utilizador pediu X", "o utilizador reparou Y"), o que não faz qualquer sentido para um documento que vou levar à defesa como o meu próprio raciocínio. Reescrevi tudo em primeira pessoa, mantendo os factos, datas e números tal como estavam — só mudei quem está a falar.

A questão que me ficou na cabeça depois disso foi outra: a app funciona bem num browser, mas para uso a sério no dia a dia — eu próprio a usar, ou alguém a testar no telemóvel durante a apresentação — um site normal nunca vai parecer tão prático como uma app instalada. Tinha duas coisas em mente ao mesmo tempo, que só por coincidência apareceram na mesma pergunta: queria que a app se sentisse mais "app" a usar (ícone no ecrã principal, sem a barra do browser à volta), e queria também que quem for assistir à apresentação consiga mesmo abrir isto e mexer, não só ver-me a fazer scroll num ecrã partilhado.

Para a primeira parte, pensei em duas hipóteses: construir uma app nativa a sério (React Native, ou envolver o que já tenho com Capacitor), ou transformar o que já existe numa PWA. Descartei a app nativa quase de imediato — seria reescrever a interface outra vez, ou pelo menos embrulhá-la, e ainda por cima teria de publicar nas lojas de apps (contas de developer, revisão, tudo isso) só para uma demonstração escolar. Não vale o esforço para o que preciso. Uma PWA resolve a mesma necessidade com uma fração do trabalho: um `manifest.json` com o nome, os ícones (já tenho a marca CentiSible pronta, é só aplicar) e a cor de tema oliva, mais um service worker mínimo — o `vite-plugin-pwa` trata da maior parte disto sozinho. Com isso já dá para "Adicionar ao ecrã principal" no telemóvel ou no computador e abrir num modo próprio, sem parecer que é só mais um separador do Chrome.

A segunda parte é onde as coisas complicam — uma PWA instalada continua a precisar de um sítio real para ir buscar a app, não adianta nada se só corre na minha máquina. Isto liga-se a uma pesquisa que já tinha feito sobre alojamento: já tenho o `docker-compose.prod.yml` pronto e testado, falta só decidir onde o pôr a correr (Railway, Render, Fly.io, um VPS da Hetzner) e configurar um domínio. Também tinha perguntado especificamente pela Vercel, e a resposta ficou clara — o frontend encaixaria bem lá (é só um build Vite normal), mas o backend não, sem mexer em três coisas que hoje dependem de o processo estar sempre vivo: a limpeza periódica de tokens (corre numa tarefa de fundo dentro do próprio processo), os recibos anexados (guardados em disco local, que desaparece entre pedidos num ambiente serverless) e o rate limiting (guardado em memória, sem estado partilhado entre instâncias). Para o número de pessoas que vai usar isto — a apresentação, e depois eu próprio — nenhuma dessas limitações é grave, mas explicam porque é que a Vercel não é um "encaixa e pronto" para o backend.

Não fiz nada disto ainda, ficou só a decidir: começar pela PWA primeiro (não depende de mais ninguém, dá para fazer já), escolher onde alojar, e perceber se preciso das duas coisas prontas antes da apresentação ou se uma já chega.

---

## 2026-08-29 — Nova paleta de marca: "Oliva" (verde profundo + âmbar raro)

Ideia: repensar as cores da app — inspirado num mockup que tinha (`exemplo.png`) e nas cores de uma caixa agrícola (verde, laranja, amarelo, vermelho). Antes de mexer em código, montei um artefacto (`Paletas CentiSible`) com **três direções concretas** e pré-visualizações reais em claro/escuro, para decidir com base em algo visto, não só em hexadecimais. As três mantinham verde como cor de marca mas resolviam de formas diferentes um problema real que tinha identificado primeiro: **o vermelho e o verde já têm significado nesta app** (despesa/receita, avisos de plafond) — se a marca também fosse vermelha/verde/amarela, um cartão verde deixava de se distinguir de "isto é boa notícia". Escolhi a **Opção A — "Oliva"**: verde profundo e contido (mais "floresta" que o verde-esmeralda já usado para receitas), com âmbar como acento raro, a mudança mais discreta e elegante das três.

**Apliquei a sério** (`src/index.css`, `:root` + `[data-theme="dark"]` + a media query do sistema): `--accent`/`--accent-strong`/`--accent-soft`/`--accent-foreground` passaram de violeta para verde (claro `#1f7a4c`/`#155e3a`/`#dcf2e3`; escuro `#4ade80`/`#86efac`/`#16301f`) — e, porque é a mesma variável em todo o lado, todas as utilities Tailwind derivadas (`bg-accent`, `text-accent-strong`, `border-accent`, etc.) mudaram sozinhas em todas as páginas, sem eu tocar em cada ficheiro. Os neutros (`--canvas`, `--surface`, `--border`, `--ink`...) ganharam um viés muito leve para verde em vez de cinzentos puros — "escolher o neutro, não herdá-lo".

`--accent-teal` (o antigo secundário, violeta→teal) **renomeei** para `--accent-amber` em vez de só mudar de valor — manter um nome "teal" a apontar para uma cor âmbar teria confundido quem mexesse nisto depois. Migrei em `logo.tsx`, `.brand-gradient`, `favicon.svg` (regenerado à mão, cores fixas) e `features/recurring/merchant-icons.ts` (as duas cores que usavam o acento da app como base — "Renda" e o crachá genérico — não as marcas reais tipo Netflix/MEO, essas mantêm as suas cores verdadeiras mesmo que isso signifique dois verdes parecidos por perto).

**Redesenhei o logótipo para a paleta nova, não só o recolori**: o gradiente do "C" deixou de ser verde→azul→violeta (a paleta antiga) e passou a verde→verde-escuro (`--accent` → `--accent-strong`, a mesma dupla usada em todo o resto da app). A moeda (o "pontinho") deixou de ser violeta e passou a **âmbar** — um cêntimo dourado dentro de um "C" verde faz mais sentido temático do que tudo na mesma cor, e cria uma segunda leitura de cor deliberada (verde = crescimento, âmbar = a própria moeda).

**Verifiquei que nada ficou preso à paleta antiga**: procurei por todos os hexadecimais antigos (`#6552f5`, `#8c7bff`, `#14b8a6`, `#2dd4bf`, etc.) e por `accent-teal` no código todo — zero ocorrências depois da migração. `CATEGORY_COLOR_PALETTE` (as 8 cores à minha escolha para as próprias categorias) ficou **intencionalmente por tocar** — são cores de personalização, não de marca, e o violeta/teal continuam a ser duas boas opções entre oito, independentemente da cor da app.

**Validação**: `tsc`/`oxlint`/`vite build` limpos. Verifiquei visualmente com Playwright em claro e escuro (painel, login, landing), incluindo um teste explícito da cor computada de um crachá (`getComputedStyle` devolveu `rgb(31, 122, 76)` = `#1f7a4c`, exatamente o valor esperado) para não confiar só na leitura visual de uma screenshot pequena. Suite E2E completa: 9/9 a passar. Sem alterações ao backend.

---

## 2026-08-29 — "Recarregar plafond" nos cartões pré-pagos, com o formulário já preenchido

Ideia: nos cartões do tipo pré-pago (ex: Universo), quando o saldo está abaixo do plafond, ter um botão "Recarregar plafond" que leva logo à criação da transação já com os dados preenchidos (conta, tipo), faltando só o que for mesmo preciso preencher à mão.

**Onde aparece**: `features/accounts/card-status.tsx` (`CardStatus`, partilhado entre o cartão de conta do painel principal e a linha de conta em Contas) — o botão só aparece quando `below` já era verdadeiro (saldo < plafond), mesmo sítio onde já vivia "Abaixo do plafond". Pré-preenche: conta (a do próprio cartão), tipo "Receita", valor = exatamente o que falta para atingir o plafond (`plafond - saldo_atual`, o mesmo cálculo já usado no aviso "falta recarregar X€" do Insights), e uma descrição "Recarga de plafond". Categoria e data ficam por preencher — não há forma fiável de adivinhar a categoria certa, e a data já vem com o dia de hoje por omissão no formulário.

**Como os dados viajam entre páginas**: `navigate('/transacoes', { state })` (o `state` de navegação do React Router, mesmo mecanismo já usado no redirecionamento pós-login) — sem endpoint novo nem query string. `routes/transactions-location-state.ts` (novo, módulo mínimo só com o tipo) evita que `card-status.tsx` tivesse de importar a página toda de Transações só para o tipo do `state`.

**Bug real que encontrei e corrigi durante a verificação** (não teria aparecido sem testar a sério com Playwright): o formulário abria pré-preenchido durante ~50ms e depois fechava sozinho — via `navigate(location.pathname, { replace: true, state: null })` dentro de um `useEffect` para limpar o `state` do histórico (impedir que "recuar" no browser reabrisse o mesmo formulário). Essa chamada a `navigate()`, dentro da árvore de `AnimatePresence`+`Suspense` do `ProtectedRoute` (ver entrada de hoje sobre a reestruturação de rotas), acabava por repor o `TransactionsPage` ao estado inicial. Corrigi a limpar a entrada do histórico diretamente (`window.history.replaceState({ ...window.history.state, usr: null }, '', window.location.href)`) em vez de passar pelo `navigate()` do router — não dispara nenhuma navegação reativa nem re-render, só corrige o que fica guardado para trás. Confirmei com um script à parte que lia `window.history.state` e a presença do campo do formulário em vários instantes: antes da correção, o campo desaparecia entre os 50ms e o 1s; depois, ficava.

**Validação**: `tsc`/`oxlint`/`vite build` limpos. Verifiquei ponta a ponta com Playwright, incluindo forçar um cenário real de "abaixo do plafond" (a conta de demonstração estava com o saldo exatamente igual ao plafond, o que escondia o botão de propósito — criei e depois apaguei uma transação de teste para validar com um défice real) — botão a aparecer só quando devido, formulário a abrir com os valores certos (conta, tipo, valor), a ficar aberto, e a submissão a funcionar de ponta a ponta. Suite E2E completa: 9/9 a passar.

---

## 2026-08-29 — Painel principal: ordem diferente em mobile

Reparei que em mobile "Próximos pagamentos" ficava no fundo da página — depois do gráfico de despesas e dos objetivos — o que não era prático para o conteúdo mais urgente de ver. Antes de mexer, pensei bem em como reordenar: separar o conteúdo urgente (Insights, Próximos pagamentos) do conteúdo para explorar com calma (gráfico de despesas, Objetivos), com o segundo grupo atrás de um separador simples em vez de mais scroll — só para os dois cartões onde esconder atrás de um toque não custa nada (ninguém precisa de ver o gráfico ao primeiro relance todos os dias, ao contrário de um alerta ou de uma fatura a vencer).

**Mudança**: só a versão mobile (abaixo do breakpoint `xl`, o mesmo já usado nas outras reformulações responsivas desta sessão) muda de ordem — o desktop fica exatamente igual, não era um problema ali. Em mobile, depois dos cartões de saldo: **Insights → Próximos pagamentos → separador "Despesas / Objetivos"** (antes: gráfico → Insights → Objetivos → Próximos pagamentos). O separador reutiliza o mesmo estilo do seletor "Individual / Agregado familiar" que já existia no painel — consistência em vez de inventar um padrão novo.

**Decisão de implementação**: em vez de tentar reordenar com CSS `order` dentro de uma grelha partilhada entre desktop e mobile (a estrutura desktop pareia Gráfico+Insights numa linha e Objetivos+Pagamentos noutra — trocar a ordem em mobile precisa de tirar Insights e Pagamentos dessas pareações), passei a ter dois blocos JSX separados — um `hidden xl:flex` com a grelha 2×2 de sempre, outro `flex xl:hidden` com a nova ordem mobile — escondidos/mostrados por CSS consoante o breakpoint. Seguro porque nenhum dos cartões envolvidos tem estado ou pedidos próprios (todos recebem os dados por prop vindos do `DashboardPage`); duplicar a árvore de JSX entre os dois blocos não duplica pedidos à API nem estado, só um pouco de trabalho de render a mais — troca aceitável para não ter de forçar uma reordenação por CSS mais frágil. Dividi `GoalsSummaryCard` em `GoalsList` (conteúdo puro, sem `<Card>` à volta) + o wrapper de sempre, para o mesmo conteúdo poder ser reutilizado dentro do separador mobile sem meter um `<Card>` dentro doutro.

**Validação**: `tsc`/`oxlint`/`vite build` limpos. Verifiquei com Playwright em mobile (390px) — ordem nova confirmada, separador a trocar entre "Despesas" e "Objetivos" corretamente — e em desktop (1600px), para confirmar que ficou pixel-a-pixel igual ao que já estava. Suite E2E completa: 9/9 a passar.

---

## 2026-08-29 — Logótipo definitivo: o "C" com o gráfico dentro

Tinha `logotipostyle.png` — um style guide completo com o logótipo oficial da marca: um "C" grosso e aberto (a letra), com um gráfico de barras ascendente e uma moeda (o "pontinho") desenhados dentro do espaço que a letra fecha. A própria imagem explica a composição: "Letra C + Gráfico (evolução e crescimento) + Moeda (o centro de tudo) = CentiSible". Substitui o símbolo anterior (uma moeda genérica com "¢" no meio, que tinha feito antes de ter uma referência de marca).

**Desenho**: `components/logo.tsx` — o "C" é um `<path>` com um arco (`A 10.5 10.5 ...`), não um círculo tracejado: dá-me controlo exato sobre onde fica a abertura (à direita, ~68°) e o arredondamento das pontas (`stroke-linecap="round"`). Gráfico: 4 retângulos com altura crescente. Moeda: um círculo cheio no canto superior esquerdo do espaço interior. Gradiente diagonal (topo→fundo) a três cores — `var(--accent-teal)` → azul fixo (`#3b82f6`, novo, só existe dentro do símbolo) → `var(--accent)` — os extremos continuam a ser os tokens já estabelecidos (adapta-se a claro/escuro sozinho), só o azul intermédio é novo. O gráfico de barras usa o mesmo gradiente (fica em ombre, barras mais altas mais para o lado azul/violeta); a moeda usa `var(--accent)` sólido, para não competir com o gradiente do anel.

**Alcance da mudança — só o símbolo, não a paleta da app**: tal como da vez anterior com o `exemplo.png` (cards do painel), esta imagem serviu de referência para o *logótipo*, não para repintar a aplicação inteira a verde/azul/violeta — a app continuava violeta/teal em todo o lado, `.brand-gradient` (usado no texto do hero da landing, por exemplo) ficou tal como estava. Só o símbolo da marca mudou nesta entrada (a paleta inteira só mudaria mais tarde, na entrada "Oliva").

**Todos os sítios onde a marca aparece** — como `Logo`/`LogoMark` são um componente partilhado, mudar `logo.tsx` propagou sozinho a `app-shell.tsx` (sidebar), `splash.tsx` (ecrã de carregamento), `landing.tsx` (topo e rodapé), `login.tsx` e `register.tsx`. Só o favicon (`public/favicon.svg`) é um SVG estático à parte, sem acesso às variáveis CSS da app — regenerei-o à mão com o mesmo desenho e as mesmas cores em hexadecimal fixo (equivalentes ao tema claro).

**Validação**: `tsc`, `oxlint` e `vite build` limpos. Verifiquei visualmente com Playwright — zoom à marca isolada, e a aparecer corretamente na landing, login, sidebar autenticada e no separador do browser (`/favicon.svg` renderizado a 400×400 para confirmar o desenho ao pormenor). Suite E2E completa: 9/9 a passar.

---

## 2026-08-29 — Detalhe da transação passou de painel embutido a modal

Reparei, em mobile, ao clicar numa transação já scrollada lá para baixo, que o painel de detalhe aparecia no topo da página (era a primeira coisa dentro do `<main>`) — tinha de subir tudo para o ver, o que não fazia muito sentido.

**Causa**: o painel de detalhe substituía o cartão "Nova transação" na coluna da direita, que em mobile (sem `lg:flex-row-reverse`) fica ANTES da lista no fluxo normal da página — nada scrollava sozinho, mas o conteúdo que aparecia por cima da posição atual de scroll ficava fora do ecrã.

**Correção**: `TransactionDetailPanel` (inalterado) passou a ser mostrado dentro de um `TransactionDetailModal` novo — overlay fixo ao ecrã (`position: fixed`, independente de onde a página estava scrollada), fundo semitransparente, a fechar ao clicar fora (comparação `e.target === e.currentTarget` no backdrop, sem precisar de `stopPropagation` no cartão) ou na cruz. Mesmo padrão já usado no `MobileDrawer` do `app-shell.tsx` (`AnimatePresence` com um backdrop + conteúdo, ambos `motion.div`). Usei em todas as larguras de ecrã, não só mobile — simplifica (um único caminho de render em vez de duas versões a manter) e um modal centrado para ver o detalhe de um registo é um padrão perfeitamente normal em desktop também.

**Validação**: `tsc`/`oxlint`/`vite build` limpos. Verifiquei com Playwright em mobile (390px): scroll a 2500px, clique numa transação por coordenadas de rato (não `locator.click()`, que faz auto-scroll-into-view e mascarava o próprio bug que queria testar) — o modal abre exatamente por cima do scroll atual (`window.scrollY` não muda: 2500 antes, durante e depois de fechar). Confirmei também em desktop (1440px): modal centrado, sem interferir com o painel "Nova transação". Suite E2E completa: 9/9 a passar.

---

## 2026-08-29 — Transações agrupadas por dia, painel de detalhe e recibos anexados

Ideia, com mais três imagens de referência que tinha (`exemplo2.png`, `exemplo3.png`, `exemplo4.png`): agrupar a lista de Transações por dia ("Hoje", "Ontem", ...), clicar numa transação para ver um cartão com os seus dados, e poder anexar uma foto/PDF do recibo a uma transação.

**Pensei bem antes de começar**: as duas primeiras são polimento de UX de baixo risco e valem a pena; os recibos são a mais valiosa das três para um utilizador real (prova de compra) mas a única que precisa de infraestrutura a sério (armazenamento de ficheiros) — decidi manter simples (disco local, sem serviço externo). **Não construí**: "Dividir despesa" (split expense) que aparecia no mesmo cartão nas imagens — é um pedido separado e bem maior (dividir uma transação em várias), fora do que estava a fazer aqui.

**Agrupamento por dia**: `lib/month.ts` ganhou `dayGroupLabel()` — "Hoje"/"Ontem"/"25 de agosto" (ano só aparece se não for o atual). A lista já vinha ordenada por data decrescente do backend (`transaction_repository.list_by_user`), por isso agrupar foi só juntar itens consecutivos com a mesma data — sem pedir nada de novo à API.

**Painel de detalhe**: a página já tinha duas colunas (lista + "Nova transação" fixa à direita) — em vez de acrescentar uma terceira zona, o painel da direita passou a ser um de três estados mutuamente exclusivos: formulário de criação, painel de detalhe da transação selecionada, ou o botão "Adicionar transação". Clicar numa linha da lista abre o detalhe; o antigo comportamento de "Editar"/"Eliminar" inline em cada linha (expandia a própria linha num formulário) removi da lista e passou a viver dentro do painel de detalhe — simplifica a linha (fica só ícone + nome + valor + hora, como nas imagens) e não há duas formas diferentes de editar a competir.

**Crachá de categoria em vez de adivinhar a marca**: ao contrário do "Próximos pagamentos" do painel principal (onde as recorrências não têm necessariamente uma categoria visível ali), uma transação já lançada tem sempre a categoria que escolhi — com ícone emoji e cor já configurados na página Categorias (funcionalidade de sessões anteriores). A lista e o painel de detalhe reutilizam isso diretamente (círculo colorido com o emoji da categoria), mais correto do que tentar adivinhar pela descrição.

**Recibos — decisão de esquema**: um recibo por transação, guardado em disco (`backend/uploads/receipts/<id-da-transação>`, sem extensão — só o `Content-Type` fica na base de dados, `receipt_content_type`, e sirvo com esse header independentemente do nome do ficheiro). Sem `python-multipart` a app não aceita `UploadFile` — primeira dependência nova desde o início do projeto. Tipos aceites: JPEG/PNG/WEBP/PDF, até 8MB. Endpoints novos, todos autenticados e a verificar que a transação me pertence: `POST/GET/DELETE /transactions/{id}/receipt`. **Sem `StaticFiles`**: servir os ficheiros por um mount estático exporia por URL previsível (mesmo com UUID) sem o mesmo controlo de acesso que todos os outros recursos da app já têm — o endpoint de download lê o ficheiro e confirma o dono antes de o devolver, como tudo o resto.

**Armadilha que evitei — `<img src>` não leva Authorization**: o access token vive em memória (não em cookie), por isso um `<img src="/api/v1/transactions/x/receipt">` direto nunca autenticaria o pedido. `api/client.ts` ganhou `uploadFile()` (multipart, sem `Content-Type` manual — o browser trata do boundary) e `fetchBlob()` (GET autenticado que devolve um `Blob`); o painel de detalhe busca o recibo como blob e cria um `URL.createObjectURL` local, revogado com `useEffect` quando a imagem deixa de ser precisa.

**Anexar já na criação**: `TransactionForm` (reutilizado para criar e editar) ganhou um campo de ficheiro opcional — ao submeter, cria/atualiza a transação primeiro e só depois faz o upload do recibo com o id que voltou, exatamente como queria ("adicionar ao criar transações").

**Infraestrutura**: volume `uploads_data:/app/uploads` novo em `docker-compose.yml` e `docker-compose.prod.yml`, para os recibos sobreviverem a reinícios do container.

**Validação**: backend — 10 testes novos (`test_transaction_receipts.py`: upload+download, tipo não suportado, ficheiro grande a mais, sem recibo dá 404, apagar recibo, apagar transação apaga o ficheiro do disco, isolamento entre utilizadores, autenticação obrigatória) com `uploads_dir` isolado por teste via `monkeypatch`+`tmp_path` — 231 testes a passar, `ruff` limpo (precisou de acrescentar `fastapi.File` à lista de chamadas imutáveis do bugbear, mesmo padrão já usado para `Depends`/`Query`). Frontend — `tsc`/`oxlint`/`vite build` limpos. Verifiquei visualmente com Playwright: agrupamento por dia correto, criar transação com recibo anexado, clicar para abrir o detalhe com o recibo a aparecer (imagem em miniatura). Suite E2E completa: 9/9 a passar — a reestruturação da página (remover edição inline, novo painel) não partiu o fluxo existente.

---

## 2026-08-29 — CentiSible Insights, Próximos pagamentos e navegação sem "piscar"

Quatro coisas para o painel principal: (1) uma secção "CentiSible Insights" (já existia como "Alertas do mês" — só faltava o nome novo); (2) um cartão "Próximos pagamentos" com o total, data e ícone/marca de cada despesa recorrente por vir; (3) usar `exemplo.png` (mockup que já tinha, com a marca CentiSible) como referência visual para o layout e manter os cartões genericamente do mesmo tamanho; (4) animação de transição suave ao mudar de página, em vez do ecrã a "piscar" quando os dados atualizam.

**`exemplo.png`**: mockup de referência com painel em duas linhas de dois cartões simétricos — (Despesas por categoria | CentiSible Insights) e (Objetivos | Próximos pagamentos). O layout anterior tinha uma coluna esquerda alta (Insights+Objetivos empilhados) contra o gráfico à direita — assimétrico. Restruturei para bater certo com o mockup: duas grelhas `xl:grid-cols-2` separadas, cada uma com `items-stretch` (por omissão, sem o `items-start` que lá estava antes) para os dois cartões de cada linha ficarem sempre com a mesma altura. **Cor mantida** (violeta→teal já estabelecido, não o verde do mockup) — o mockup serviu de referência de layout/estrutura, não de repintura da app; já tinha aprovado a paleta atual nesta mesma sessão.

**"Próximos pagamentos"**: novo cartão em `dashboard.tsx`, reaproveita `listRecurring()` (mesma chave `['recurring']` de `routes/recurring.tsx`, cache partilhada — nenhum endpoint novo no backend). Filtra recorrências ativas com `next_occurrence` dentro de 30 dias, ordena por data, soma o total (mesmo que só mostre as 5 primeiras linhas). Cada linha tem um crachá circular colorido + ícone + nome + data curta ("3 set") + valor.

**Ícones de marca — decidi conscientemente não reproduzir logótipos reais**: em vez de recriar os logótipos de Vodafone/NOS/MEO/Netflix/Spotify/etc. (marcas registadas, risco de direitos de autor desnecessário para um projeto escolar), `features/recurring/merchant-icons.ts` faz correspondência do nome da recorrência (regex simples, case-insensitive) a um ícone genérico do Lucide (telemóvel para operadoras, carrinho para supermercados, música para Spotify, ...) pintado com a cor mais associada a cada marca — reconhecível ao relance sem replicar a identidade visual de ninguém. Sem correspondência, cai num crachá genérico (ícone de repetição, cor da marca da app).

**Navegação sem "piscar" — encontrei duas causas reais, não uma só**:
1. **`AppShell` remontava a cada navegação** — `ProtectedRoute` embrulhava cada `<Route>` individualmente (`<Route path="/contas" element={<ProtectedRoute><AccountsPage/></ProtectedRoute>} />`, repetido 10×), por isso a sidebar inteira desmontava e remontava a cada clique no menu, e o `<Suspense fallback={<Splash/>}>` também estava no topo, cobrindo o ecrã todo (sidebar incluída) com o spinner de carregamento a cada troca de página. Corrigi com o padrão de **rota de layout** do React Router: `ProtectedRoute` passou a ser um único `<Route element={<ProtectedRoute/>}>` com as 10 páginas como filhas (`<Outlet/>`), montado uma vez por sessão autenticada. A transição (`AnimatePresence`+`motion.div`, fade+slide de 8px) e o `Suspense` moveram-se para dentro do `ProtectedRoute`, à volta só do `<Outlet/>` — a sidebar nunca mais desaparece, só o conteúdo por baixo transita. Ganho lateral: o flip-in da marca na sidebar (`Brand`, em `app-shell.tsx`) passou a ser seguro de ativar (antes tinha ficado sem animação de propósito, exatamente por causa deste remount) — agora só acontece uma vez por sessão, como no login/registo/landing.
2. **React Query a mostrar um ecrã em branco durante um refetch** — trocar de mês ou de vista (individual/agregado) no painel, ou o filtro de mês em Orçamentos/Histórico/Transações, muda a `queryKey`, e por omissão o React Query esvazia `data` enquanto a nova página carrega — o conteúdo desaparecia e reaparecia de repente. Corrigi com `placeholderData: keepPreviousData` (TanStack Query v5) nessas queries: os dados antigos ficam visíveis, com uma leve transição de opacidade (`isFetching` → `opacity-60`, 300ms) em vez de um vazio súbito.

**Validação**: `tsc`, `oxlint` e `vite build` limpos. Verifiquei visualmente com Playwright: layout 2×2 simétrico, crachás de marca corretos (Netflix a vermelho, recorrência sem correspondência com o crachá genérico), navegação Painel→Contas→Categorias sem a sidebar a desaparecer, e troca de mês no painel sem ecrã em branco (dados antigos visíveis até os novos chegarem). Suite E2E completa: 9/9 a passar — a reestruturação de rotas (a mudança com mais risco de partir algo) não quebrou nenhum fluxo. Backend inalterado nesta entrada: 221 testes a continuar a passar.

---

## 2026-08-29 — Rebatizado para CentiSible, com logo dinâmico novo

Ideia: mudar o nome de "FinTrack" para "CentiSible" (jogo de palavras: "cent" — a unidade de dinheiro — + "sensible") e desenhar um logo novo, dinâmico, para o substituir.

**Marca anterior**: um quadrado com o gradiente de marca e a letra "F" a branco, repetido de forma inline (copiado e colado) em 5 sítios diferentes — `app-shell.tsx` (sidebar), `landing.tsx`, `login.tsx`, `register.tsx` e `splash.tsx` — cada um com o seu próprio tamanho.

**Logo novo**: em vez de outra letra genérica num quadrado, uma **moeda** com o sinal de cêntimo ("¢") ao centro — literal ao "Centi" do nome. SVG desenhado à mão (`components/logo.tsx`): círculo com o gradiente violeta→teal já estabelecido (`--accent` → `--accent-teal`, a mesma identidade "fintech premium", só o desenho da marca é novo — não se justificava deitar fora uma paleta testada), rebordo denteado (`stroke-dasharray`) a imitar o friso de uma moeda a sério, e o "¢" desenhado com `<text>` em Space Grotesk (a fonte de display já usada no resto da app) em vez de um path à mão — mais simples e continua nítido em qualquer tamanho. `useId()` do React gera o id do gradiente para não colidir quando a marca aparece montada mais do que uma vez ao mesmo tempo.

**"Dinâmico" — onde faz sentido e onde não**: a app tem duas naturezas de aparição da marca. No `Splash` (ecrã de carregamento — verificação de sessão no arranque, rotas lazy) a moeda **gira continuamente** (`rotateY: 360`, loop linear) enquanto se espera — motivo óbvio para movimento contínuo, é literalmente um indicador de "a decorrer". Na landing/login/registo a moeda **assenta com um "flip" de uma vez só** ao carregar a página (`rotateY` de -110° a 0°, easing com *overshoot* a imitar uma moeda a cair e a assentar) — só a primeira impressão, não se repete. Na sidebar (`app-shell.tsx`) a marca fica **estática, sem animação nenhuma** — decisão deliberada: o `AppShell` remonta a cada navegação (`ProtectedRoute` embrulha cada `<Route>` individualmente), por isso repetir o flip a cada clique no menu ficaria cansativo em vez de elegante. `useReducedMotion()` desliga todas as animações, mostrando logo o estado final — mesmo padrão já usado no resto da app.

**Consistência à volta do nome**: `index.html` (`<title>`), favicon (`public/favicon.svg`, agora a mesma moeda em vez do relâmpago por omissão do template Vite que lá estava), a chave do `localStorage` do tema (`fintrack-theme` → `centisible-theme` — reset da preferência guardada é aceitável, é um projeto pessoal), título/descrição da API FastAPI (Swagger em `/docs`), `README.md` (raiz e `frontend/`), `docs/ARCHITECTURE.md`. **Decidi conscientemente não mudar**: `name = "fintrack-backend"` no `pyproject.toml` do backend — é só metadata interna do pacote Python (usada pelo `uv`/venv), não aparece a nenhum utilizador nem avaliador, e mudar arriscava mexer no lockfile sem benefício real. As entradas antigas deste diário também não as reescrevi — são um registo histórico do que o projeto se chamava na altura, ver a nota no topo do ficheiro.

**Armadilha que encontrei e corrigi**: o `docker-compose.yml` só faz bind-mount de `frontend/src` e `frontend/public` — o `index.html` fica "cozido" na imagem do container e não reflete edições locais como o `src`/HMR faz. A mudança do `<title>` só apareceu depois de `docker compose build frontend && docker compose up -d frontend`. Vale a pena lembrar para a próxima vez que `index.html` precisar de mudar.

**Validação**: `tsc`, `oxlint` e `vite build` limpos (zero avisos novos). Backend: 221 testes a passar, `ruff` limpo (só o `title`/`description` da app FastAPI mudaram, sem lógica tocada). Verifiquei visualmente com Playwright — logo animado a aparecer corretamente na landing, login, registo e sidebar, com zoom à própria marca para confirmar o desenho (rebordo denteado + "¢" legível). Suite E2E completa: 9/9 a passar.

---

## 2026-08-29 — Validade e plafond de cartões, com alertas em Insights

Depois de esclarecer para mim próprio o que queria: dois comportamentos distintos consoante o tipo de conta. "Cartão de banco normal" (`BANK`) — só validade + aviso perto da data. Cartões pré-pagos como o "Universo" (modelados como `CREDIT_CARD` neste esquema) — validade + **plafond mensal**: um valor que a conta deve ter, com aviso se o saldo cair abaixo.

**Decisão de esquema**: dois campos novos e opcionais em `Account` — `card_expiration_date` (Date) e `card_plafond` (Numeric(12,2)) — em vez de um novo `AccountType` ou de um mecanismo de "data de recarga" à parte. A presença de `card_plafond` já sinaliza "isto é um pré-pago com teto esperado", sem precisar de mais um enum; e o aviso é recalculado a cada visita ao painel (via `Insights`) em vez de depender de uma data de recarga fixa — mais simples e sempre correto, não preciso de manter uma data sincronizada com quando realmente recarrego. Migração `a191e332ea1c` (segue `268124a9d9c3`).

**Semântica de update importante**: ao contrário de `name`/`type`/`initial_balance` (onde `null` no PATCH significa "não mexer"), nestes dois campos `null` é um destino válido — desligar o plafond de uma conta, por exemplo. Distingui com `model_fields_set` do Pydantic em vez do padrão "None = não mexer" já usado nos outros campos, para não introduzir um campo boolean extra por campo.

**Alertas** (`insights_service.py`, mesmo motor que já gera os avisos de orçamento/objetivos): `card_expiring_soon`/`card_expired` (janela de 30 dias) e `card_below_plafond` (saldo atual < plafond). Só na vista do mês atual — mesmo critério já usado para os objetivos, porque saldo/validade são estado "agora", não do mês em navegação.

**Frontend**: `AccountForm` mostra o campo de validade para contas `BANK`/`CREDIT_CARD` e o de plafond só para `CREDIT_CARD` (visibilidade condicional via `watch('type')` do react-hook-form). Novo componente partilhado `features/accounts/card-status.tsx` — badge de validade (verde/âmbar/vermelho consoante a proximidade) e barra de progresso do plafond — usado tanto no cartão da página Contas como no cartão do painel principal, para ver o aviso onde quer que esteja, sem esperar por "Alertas do mês".

**Validação**: backend — 11 testes novos (`test_insights.py`: expira em breve/já expirou/longe (sem alerta)/abaixo do plafond/no plafond (sem alerta)/só no mês atual; `test_accounts.py`: criar com campos, omitir (fica null), atualizar, limpar explicitamente com `null`, omitir no update não mexe) — 221 testes a passar, `ruff` limpo, migração aplicada e confirmada contra a BD real. Frontend — `tsc`, `oxlint` (um aviso novo de `Date.now()` impuro corrigido com o mesmo padrão `useMemo` já usado em `dashboard.tsx` para "hoje") e `vite build` limpos. Verifiquei visualmente com Playwright: editei a conta "Universo" (demo) para plafond 1000€ e validade a 9 dias — badge âmbar + barra de progresso a aparecer corretamente na página Contas e no painel principal, e os dois alertas ("expira em breve" + "abaixo do plafond") a aparecer em "Alertas do mês". Suite E2E completa: 9/9 a passar.

---

## 2026-08-29 — Cards de saldo por conta no painel principal

Ideia: mostrar no painel principal um cartão por conta com o saldo disponível (ex.: Revolut, Universo), como ponto de partida para depois tratar do caso mais complexo dos cartões de crédito (plafond, data de expiração, data de recarga, aviso de saldo baixo — ver "Próximos passos").

**Implementação**: `ACCOUNT_TYPE_ICONS` (mapa tipo de conta → ícone `lucide-react`) estava definido só dentro de `routes/accounts.tsx`; extraí para `features/accounts/icons.ts` para ser partilhado sem duplicar, e atualizei `accounts.tsx` para importar de lá. Novo `AccountsSummaryCard`/`AccountCard` em `dashboard.tsx`: grelha responsiva (`grid-cols-1 sm:grid-cols-2 xl:grid-cols-4`) de cartões com ícone por tipo, nome e saldo atual com `AnimatedNumber` (mesmo componente de contagem usado no resto do painel), saldo negativo a vermelho. Busca as contas com `useQuery({ queryKey: ['accounts'], ... })` — mesma chave de `routes/accounts.tsx`, cache partilhada. Coloquei a secção logo a seguir ao cabeçalho do painel, antes do seletor de mês, para ficar visível de imediato.

**Validação**: `tsc -b`, `oxlint` e `vite build` limpos (só avisos pré-existentes, nenhum novo). Verifiquei visualmente com Playwright em 1920px e 390px (login real com a conta de demonstração `antonio@teste.com`, que entretanto já tem 3 contas — Conta Principal, Revolut, Universo) — cartões corretos em ambas as larguras, sem erros de página. Suite E2E completa: 9/9 a passar.

**Próximos passos — decidir antes de implementar**: a parte de "plafond"/expiração/recarga/aviso para cartões (ex.: cartão pré-pago "Universo" com limite de 1000€, aviso se não estiver lá o valor) exige campos novos no modelo `Account` — decisão de esquema difícil de reverter depois. Por esclarecer: aplica-se só a `CREDIT_CARD` ou também a outros tipos pré-pagos? "Data de expiração" é a validade física do cartão? A "recarga" deve aproveitar o sistema de recorrências/insights já existente ou ser um campo novo e independente?

---

## 2026-08-29 — Navegação persistente, números animados e limite ao histórico de transações

Objetivo: "trabalhar na parte do frontend de toda a página" — queria algo elegante, chamativo, boas animações, atenção ao pormenor, intuitivo. Usei a skill `frontend-design`. Antes de desenhar nada, tirei screenshots do estado atual (login/registo, dashboard, transações) para perceber onde a app realmente precisava de trabalho, em vez de assumir.

**Achado principal**: a landing page (Fase 13) já estava bem cuidada — paleta violeta/teal, tipografia Inter+Space Grotesk, animações — mas a app interna estava muito atrás disso: o dashboard tinha a navegação inteira como **9 links de texto sublinhados** (`text-ink-muted underline`, literalmente o estilo por omissão do browser), e as outras 9 páginas internas só tinham um link solto "Voltar ao painel" — não havia forma de ir de Orçamentos para Transações sem passar pelo dashboard primeiro. Isto era mais do que estética: era uma lacuna real de navegação.

**Decisão de direção**: evoluir a identidade visual já estabelecida (violeta/teal "fintech premium") em vez de a substituir — não se justificava deitar fora um sistema de tokens/tema claro-escuro testado e a funcionar só para "ser diferente". A mudança estrutural de maior alavancagem: uma **barra de navegação lateral persistente**.

**`components/app-shell.tsx`** (novo): sidebar fixa em desktop (`md:flex`, ícones `lucide-react` + rótulo, estado ativo com `layoutId="nav-active-pill"` do Framer Motion — a marca desliza suavemente entre itens em vez de saltar), colapsa para uma barra superior + gaveta deslizante (`AnimatePresence`) em mobile. Rodapé com avatar (iniciais), nome, email, alternador de tema e logout — tudo o que antes estava duplicado entre o cabeçalho do dashboard e nada nas outras páginas, agora vive num único sítio. Injetado num único ponto: `ProtectedRoute` passou a envolver `children` em `<AppShell>` — todas as 10 rotas protegidas ganham a navegação de uma vez, sem tocar em cada página.

**`components/page-header.tsx`**: simplifiquei — já não repete "Voltar ao painel" nem o alternador de tema (a barra lateral trata disso); ganhou um `subtitle` e um slot `actions` opcionais.

**`components/animated-number.tsx`** (novo) — a assinatura de "atenção ao pormenor" que queria: qualquer valor monetário conta a subir (spring do Framer Motion, não linear) desde 0 quando aparece, e desliza para o novo valor quando muda (trocar de mês, por exemplo). Apliquei aos cartões do dashboard, e aos valores de progresso em orçamentos e objetivos. Respeita `prefers-reduced-motion` (deriva o valor final diretamente das props em vez de passar por estado/efeito, evitando também um aviso do linter sobre `setState` dentro de `useEffect`).

**Bug real que confirmei (não um falso alarme) — `/transacoes` sem limite de datas por omissão**: a página carregava sempre *todas* as transações de sempre (sem filtro de mês por omissão); numa conta de demonstração com 12 meses de histórico isto produzia uma página de **16 710px de altura**. Corrigi com um seletor de mês (igual ao do dashboard/orçamentos) que filtra por omissão ao mês atual, e um botão "Ver todas as transações" para quando realmente precisar do histórico completo — confirmado por medição real (`document.body.scrollHeight`): 16 710px → 1 772px por omissão.

**Falsos alarmes que descartei durante a auditoria inicial** (registo aqui para não repetir a investigação): um cartão em branco na secção "Vive a dois" da landing e o gráfico de pizza do dashboard pareciam quebrados em screenshots `fullPage`/sem espera suficiente — mas ambos usam animações de entrada (`whileInView` do Framer Motion no primeiro caso, animação de entrada do Recharts no segundo) que só terminam com scroll real ou tempo de espera suficiente. Confirmei a funcionarem corretamente com scroll real e mais tempo de espera. O cartão "Poupança do mês" também pareceu com contraste lavado num screenshot — era a mesma causa (animação de entrada apanhada a meio).

**Validação**: 9 testes E2E — 3 tive de atualizar porque o cumprimento do dashboard passou a usar só o primeiro nome ("Olá, Bruno" em vez de "Olá, Bruno Login") — decisão deliberada, mais pessoal. `tsc`, `oxlint` e `vite build` limpos. Verifiquei visualmente com Playwright/Chromium em desktop (1440px), breakpoint tablet (767/800px) e mobile (390px), em tema claro e escuro.

**Por fazer, se continuar**: mais toques bespoke por página (ex: mais animação no histórico/analytics), landing/login ainda não revistos nesta ronda (já estavam bons, mas não tiveram o mesmo nível de atenção que a app interna).

**Correção no mesmo dia — espaço vazio nas páginas de lista**: reparei, com razão, que a área de conteúdo (à parte da sidebar) ficava com muito espaço morto — cada página interna continuava a centrar o seu conteúdo num `max-w-2xl`/`max-w-3xl` isolado, herdado de antes da sidebar existir, deixando uma faixa enorme vazia à direita num ecrã largo. Em vez de simplesmente alargar essa coluna única (linhas de texto longas de mais também são um problema de legibilidade), dei um propósito ao espaço: **layout a duas colunas** nas páginas do padrão "lista + formulário 'novo X'" (`accounts`, `categories`, `budgets`, `goals`, `recurring`, `transactions`): lista à esquerda (mais larga, o conteúdo principal), formulário "novo X" como painel `lg:sticky` à direita (`lg:w-80`). Implementei com `flex-col` (mobile, formulário primeiro) que passa a `lg:flex-row-reverse` (desktop) — inverte a ordem visual sem duplicar JSX nem usar `order-*` em cada filho. Em `household.tsx` (2 cartões relacionados, não lista+formulário) usei antes um `grid lg:grid-cols-2` simples.
- **Problema que descobri ao aplicar o padrão**: vários formulários internos (`CategoryForm`, `NewBudgetForm`, `GoalForm`, `RecurringForm`, `TransactionForm`) tinham grelhas `sm:grid-cols-2`/`sm:flex-row` — como essas classes reagem à largura da *viewport*, não à do contentor, ficariam a tentar pôr 2 colunas dentro de um painel lateral de 320px sempre que o ecrã tivesse ≥640px, espremendo os campos. Corrigi a forçar essas grelhas a ficarem sempre em coluna única — mais seguro e sem introduzir container queries (Tailwind v4 suporta, mas não se justificava a complexidade extra aqui) para um ganho pequeno, já que estes formulários são pequenos de qualquer forma.
- `max-w-2xl`/`max-w-3xl` das páginas afetadas subiu para `max-w-5xl`/`max-w-6xl` (transações, que tem filtros + lista + formulário, ficou com `max-w-6xl`).
- Validei visualmente (desktop 1440px com dados reais das contas de demonstração, mobile 390px a confirmar que continua tudo empilhado por ordem natural) e com a suite E2E completa (9/9, sem alterações necessárias aos testes desta vez).

**Segunda correção no mesmo dia — a primeira correção não resolveu nada, e a causa real não era largura nenhuma**: testei num ecrã largo a sério (a validação anterior tinha sido só a 1440px) e confirmei que a área de conteúdo continuava a ocupar só uma fração do ecrã, apesar do `max-w-5xl`/`max-w-6xl` de há pouco. Decidi: usar a skill de frontend a sério, reverificar em condições, e dar-me autorização para um "revamp geral" a tudo menos a sidebar.

- **Auditoria a 1920px** (nunca tinha testado a esta largura): confirmou o problema — a área de conteúdo (1664px disponíveis a par da sidebar) só tinha ~1024px de `max-w-5xl` a ser usados, e mesmo esses 1024px não estavam a ser bem aproveitados por dentro (cartões com muito ar interior). Duas frentes: (1) porque é que o `max-w` nunca era atingido; (2) o que mostrar quando finalmente for.
- **Causa raiz de (1), que encontrei só por inspeção real do DOM computado (`getBoundingClientRect`/`getComputedStyle`), não por adivinhar**: o `<main>` de cada página é filho direto de um contentor `flex flex-col` (o `AppShell`). Um item flex com `margin-inline: auto` (a classe `mx-auto`) **desliga o comportamento de esticar (`align-items: stretch`) nesse eixo** — os margens automáticos absorvem todo o espaço livre, e o item passa a dimensionar-se pelo conteúdo (shrink-to-fit) em vez de preencher o contentor. Como nenhuma página tinha `w-full` a par do `mx-auto max-w-*`, o `<main>` nunca tentava ser mais largo do que o seu próprio conteúdo — por isso **subir o `max-w-*` não tinha efeito nenhum**: nunca era o limite a segurar a largura, era a falta de `w-full` a nunca a deixar crescer até lá. Confirmei com `main.getBoundingClientRect().width` antes (1005.92px, invariável ao mudar o `max-w`) e depois (1664px = 100% do espaço disponível) da correção.
- **Correção**: acrescentei `w-full` a par do `mx-auto max-w-*` em todos os `<main>` das páginas internas (`accounts`, `budgets`, `categories`, `dashboard`, `goals`, `history`, `household`, `recurring`, `settings`, `transactions`) — uma expressão de sed em vez de 10 edições manuais, já que era o mesmo padrão em todo o lado. `max-w` subiu outra vez para valores generosos (`max-w-[2200px]` na maioria, `max-w-[2000px]` no dashboard) — agora finalmente com efeito real, a funcionar como teto para ecrãs verdadeiramente enormes, não como limite morto.
- **Lição a reter**: um item flex com margens automáticas não estica, mesmo com `align-items: stretch` implícito no contentor — `w-full` (ou `flex-1`/`self-stretch`) é sempre necessário a par de `mx-auto` quando o objetivo é "preenche até ao limite, depois centra". Isto tinha-me passado despercebido nas duas rondas anteriores de trabalho no frontend porque a validação nunca tinha corrido a mais de 1440px, onde o efeito é bem menos óbvio.

**Com a largura real disponível, revamp do conteúdo (não só esticar o que já existia)**:
- `accounts.tsx`, `categories.tsx`, `budgets.tsx`, `goals.tsx`, `recurring.tsx`: as listas de linhas finas (uma por baixo da outra, dentro de um único `<Card>`) passaram a **grelhas de cartões independentes** (`grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4`) — cada conta/categoria/orçamento/objetivo/recorrência é agora o seu próprio cartão com hover, em vez de uma linha. Isto é o que realmente resolve "espaço vazio": mais colunas em ecrãs largos, não cartões mais largos e mais vazios por dentro. `accounts.tsx` ganhou também um ícone por tipo de conta (`Landmark`/`Wallet`/`PiggyBank`/`CreditCard`, `lucide-react`).
- `dashboard.tsx`: "Alertas do mês" e "Despesas por categoria" passaram de empilhados a lado a lado (`xl:grid-cols-[1fr_1.3fr]`), o gráfico de pizza cresceu (`h-64` → `xl:h-80`), e a legenda ganhou uma mini-barra de progresso por categoria (mais um toque de "atenção ao pormenor", e enche o espaço com informação em vez de ar).
- `history.tsx`: o gráfico de evolução cresceu (`h-64` → `xl:h-96`) e o cartão de comparação com o mês anterior passou de 3 linhas empilhadas a 3 colunas lado a lado.
- **Falso alarme, desta vez confirmado com certeza** (não só suposto): o gráfico de pizza do dashboard voltou a parecer ausente num screenshot a 1920px mesmo com 1s de espera. Desta vez confirmei a sério — `svg.recharts-surface` existia sempre no DOM (7 `<path>`), e um screenshot com 3s de espera mostrou-o perfeitamente renderizado. É mesmo só o tempo que o Recharts leva a medir e pintar após montar, sem relação com a largura — não havia nada para corrigir no código.
- Validei a 1920px com dados reais (conta demo Teresa) em todas as páginas alteradas, a 390px (mobile, confirmando que continua tudo empilhado), `tsc`/`oxlint`/`vite build` limpos, e suite E2E completa 9/9 sem alterações.

**Terceira correção no mesmo dia — `AccountForm` escapou à correção dos formulários**: ao rever o resultado, reparei que o dropdown "Tipo" em "Adicionar conta" estava mal ("bugado"). Causa: `AccountForm` tinha `sm:flex-row sm:items-end` na linha Nome/Tipo/Saldo inicial/botões — exatamente o mesmo problema já corrigido em `CategoryForm`/`NewBudgetForm`/`GoalForm`/`RecurringForm` (grelha reativa à *viewport*, não ao contentor, a espremer 4 campos dentro do painel lateral de 320px), mas passou-me ao lado desta vez porque a correção anterior foi feita por procura textual de `sm:grid-cols-2`/`sm:flex-row` e o `AccountForm` já tinha sido reescrito (ícones por tipo de conta) depois dessa ronda, sem repetir a verificação. Corrigi da mesma forma — sempre em coluna única. Revi também `household.tsx` (`InviteForm`, mesma classe `sm:flex-row`) — esse fica num contentor bem mais largo (~700px+, não um painel de 320px) e não tem o mesmo problema, confirmei visualmente. **Lição**: depois de um padrão destes corrigido, vale sempre a pena voltar a grep-ar no fim de uma sessão de mudanças (`sm:flex-row`, `sm:grid-cols-2`) em vez de confiar só na lista de ficheiros já vistos.

**Quarta mudança no mesmo dia — filtros de Transações recolhidos por omissão em mobile**: em ecrã pequeno, o cartão "Filtros" (5 campos) ocupava um ecrã inteiro de altura antes de se ver sequer uma transação. O cabeçalho do cartão passou a um `<button>` clicável (chevron que roda, `lucide-react`) que mostra/esconde o conteúdo com uma animação de altura (`AnimatePresence`+`motion`, a respeitar `prefers-reduced-motion` como o resto da app). Estado inicial decidido uma vez no arranque via `window.matchMedia('(min-width: 1024px)')` — fechado em mobile (não é reativo a redimensionar a janela depois, só à largura no primeiro render, o que é suficiente aqui). Quando fechado e há filtros opcionais ativos (conta/categoria/tipo — não a data, que está sempre definida por omissão ao mês atual e não seria um sinal útil), aparece um contador junto ao título ("Filtros 1") para não esconder que há um filtro a aplicar-se. Validei com Playwright a 390px (fechado por omissão, abre ao clicar, mostra o badge) e a 1440px (continua aberto por omissão), suite E2E completa 9/9 sem alterações.

**Quinta mudança no mesmo dia — "Ver ano completo" no Histórico**: queria o padrão "‹ Mês › + Mês atual" em geral; pensei primeiro onde fazia sentido, porque o custo variava muito por página — no Histórico é uma mudança trivial (o endpoint `/analytics/monthly-trend` já aceita `months` até 24, só o frontend pedia sempre 6), no Painel exigiria um endpoint novo de agregação anual que não existe, e em Orçamentos nem faz sentido da mesma forma (cada orçamento já É de um mês específico — "ano completo" ali seria listar os 12 meses, não somar um total). Decidi fazer só o Histórico. Implementei como um botão "Ver ano completo"/"Ver últimos 6 meses" junto ao "Mês atual", a alternar `months` entre 6 e 12 no pedido à API (`getMonthlyTrend(isoMonth, fullYear ? 12 : 6)`) e o título do cartão a acompanhar. Nada no backend mudou — já suportava isto. Validei a 1920px (12 meses legíveis, gráfico com espaço de sobra) e a 390px (o Recharts esconde automaticamente etiquetas alternadas do eixo X quando não cabem, sem quebrar o layout), suite E2E 9/9 sem alterações.

**Sexta mudança no mesmo dia — Objetivos no painel principal**: com razão, o dashboard tinha Alertas e Despesas por categoria mas nada sobre objetivos, apesar de ser uma funcionalidade central (Fase 10). Novo `GoalsSummaryCard` (`routes/dashboard.tsx`) no espaço já vago da coluna esquerda mais estreita (ao lado de "Despesas por categoria"): até 3 objetivos (os não atingidos primeiro), cada um com barra de progresso animada e `AnimatedNumber` para o valor atual, link "Ver todos" para `/objetivos`, e um estado vazio com convite a criar o primeiro quando não há nenhum. Usa `queryKey: ['goals']` — a mesma chave de `routes/goals.tsx`, por isso a cache do React Query é partilhada entre as duas páginas em vez de duplicar o pedido. Sem alterações ao backend (reutiliza `GET /api/v1/goals` já existente). Validei a 1920px (com e sem objetivos) e a 390px (empilha corretamente), suite E2E 9/9 sem alterações.

**Sétima mudança no mesmo dia — bug real na fusão de "Despesas por categoria" do agregado**: apontei, com razão, que fundir categorias homónimas por nome (feito na sessão de "despesas partilhadas no agregado", mais cedo hoje) estava errado em metade dos casos. Exemplo meu: um casal que paga uma renda só deve ver "Renda" uma vez (a soma); um casal em que cada um paga a sua própria renda deve ver as duas rendas separadas — e a lógica anterior fundia sempre pelo nome, sem olhar a se a despesa era de facto partilhada (`is_shared`) ou só uma coincidência de nome entre duas despesas pessoais independentes (ex: "Alimentação" de cada um, sem ligação nenhuma uma com a outra).

- **Correção em `dashboard_repository.expenses_by_category`**: na vista de agregado, o agrupamento passou a depender de `is_shared` — despesas **partilhadas** continuam a fundir-se sempre numa única linha (somando entre todos os membros que a marcaram, seja quem for); despesas **pessoais** (a maioria, por omissão) deixam de se fundir com as de outra pessoa só por coincidência de nome — ficam uma linha por pessoa. Implementei com uma chave de agrupamento condicional (`CASE WHEN is_shared THEN NULL ELSE user_id END`) a par do nome da categoria, para que só as partilhadas caiam todas no mesmo grupo independentemente de quem as registou.
- **Novo campo `owner_name`** em `CategoryExpense` (schema + repositório + serviço): identifica de quem é uma linha pessoal na vista de agregado (`None` para partilhadas — já não pertencem a uma pessoa só — e sempre `None` na vista individual, onde não há nada a desambiguar). Nome completo do backend; o frontend usa só o primeiro nome no rótulo ("Alimentação · Teresa").
- **Bug lateral que apanhei ao mexer nisto**: a lista/gráfico de pizza no frontend usava `key={entry.name}` — com duas linhas possivelmente com o mesmo `name` agora (a mesma categoria, uma partilhada e outra pessoal, por exemplo), isto seria uma chave React duplicada. Corrigi para uma chave composta (`category_id` + dono).
- **Testes**: o teste existente `test_dashboard_household_scope_aggregates_all_members` estava a validar exatamente o comportamento errado (duas despesas pessoais "Comida" a fundirem-se numa só de 65€) — corrigi para esperar duas linhas separadas, com nomes de utilizador reais (`_make_user` usava por omissão "User" para ambos, o que teria mascarado o próprio bug se os nomes ficassem iguais). Novo teste `test_dashboard_household_merges_shared_expenses_with_same_category_name` cobre o caso inverso (duas pessoas a marcar a mesma renda como partilhada → uma linha só, `owner_name=None`) a par de uma despesa pessoal não relacionada, para confirmar que não se confundem. **210 testes a passar** (209 + 1), `ruff` limpo. Validei visualmente contra os dados reais das contas de demonstração (Antonio+Teresa): "Renda" partilhada aparece fundida sem nome, "Renda · Teresa" (não marcada como partilhada) aparece à parte, "Alimentação · Antonio" e "Alimentação · Teresa" já não se somam numa só linha enganadora. Suite E2E 9/9 sem alterações.

**"Bug" que reportei a mim próprio e que afinal não era bug — mas apanhou a poluição de dados dos testes E2E**: testei marcar uma renda de 600€ como partilhada e vi o total "Renda" a 1200€, e achei estranho. Investiguei com uma query direta à base de dados (não assumi nada): a conta do Antonio já tinha uma renda de 420€ partilhada da sessão de dados anteriores, e a nova de 600€ somou-se corretamente para 1020€ — não 1200€, e não havia bug nenhum na fusão. Pelo caminho, a mesma investigação revelou um problema real e não relacionado: a base de dados de desenvolvimento tinha **88 utilizadores fantasma** (`nome.timestamp.random@example.com`), um por cada `npm run test:e2e` corrido hoje — a suite E2E cria contas e transações reais contra a API já a correr, sem as reverter no fim (ao contrário da suite do backend, que usa uma transação com savepoints revertida sempre; ver `tests/conftest.py`). Isto é esperado/aceite (a suite E2E precisa mesmo de dados reais persistidos para poder navegar a app), mas acumula lixo a cada corrida sem limpeza manual.

**Reset das contas de demonstração + teste específico que queria fazer**: pedi a mim próprio para repor as contas de demonstração do zero com um ano de dados, e queria perceber o que aconteceria se o casal do agregado marcasse **valores diferentes** de renda partilhada (não exatamente metade cada) — exatamente o caso que a correção da fusão de categorias (entrada anterior) tinha de aguentar bem.
- Limpeza: `DELETE FROM users WHERE email LIKE '%@example.com'` (as 88 contas de teste E2E) + `DELETE FROM users WHERE email IN ('antonio@teste.com','teresa@teste.com')` — cascata `ON DELETE CASCADE` em todas as tabelas de domínio (`accounts`, `categories`, `transactions`, `goals`, `budgets`, `recurring_expenses`, `household_members`, `refresh_tokens`) apaga tudo o resto de cada utilizador automaticamente. Confirmei com uma contagem a zero em todas as tabelas antes de recriar.
- Novo script (`scratchpad/seed-demo.mjs`, não commitado, PRNG determinístico próprio em vez de `Math.random()` para ser reprodutível) regista os dois, cria o agregado, 1 conta + 8 categorias com ícone/cor cada (a usar a funcionalidade de hoje), e 12 meses de transações via a API real: ordenado de 1200€, despesas variadas por categoria, e — de propósito — **renda partilhada com valores diferentes**: 500€ do Antonio, 300€ da Teresa, todos os meses. Também um objetivo, uma despesa recorrente (Netflix) e um orçamento por pessoa.
- **Resposta à pergunta que me tinha feito**: confirmei diretamente pela API depois de gerar os dados — a vista de agregado mostra "Renda: 800,00€" (500+300, fundida, `owner_name: null`) porque ambos marcaram a despesa como partilhada. A fusão nunca assumiu partes iguais — é uma soma simples de tudo o que está marcado `is_shared=True` com aquele nome de categoria, seja qual for o valor de cada um. Bónus: o script também marca ~1/3 das faturas de "Contas e Serviços" como partilhadas, para mostrar esse mesmo padrão numa categoria com mais do que uma transação partilhada por mês.
- Validei visualmente (painel do agregado a 1920px, Histórico com "Ver ano completo") e pela API diretamente. Sem alterações de código de produção nesta entrada — só dados. `ruff`/`pytest` (210, inalterado) confirmados na mesma.

---

## 2026-08-29 — Primeira corrida real do CI: quatro bugs latentes apanhados

Fiz `git init` + primeiro commit + push e corri o workflow do GitHub Actions pela primeira vez. Como já sabia pelo roadmap, isto nunca tinha corrido a sério antes — e o processo (várias corridas, cada uma revelando o problema seguinte por baixo do anterior) apanhou quatro bugs genuínos, nenhum relacionado com o trabalho desta sessão em si, que só não apareciam porque ninguém tinha corrido isto num ambiente real de CI antes.

**Bug 1 — `test_health_check_returns_ok` fixava o literal `"development"`**: o endpoint `/health` devolve `settings.environment`, mas o teste comparava sempre contra a string fixa `"development"` em vez de ler `settings.environment`. Falha garantida em qualquer ambiente que não seja esse. Corrigi em `tests/api/test_health.py` a importar `settings` e comparar contra o valor real.

**Bug 2 — cookie do refresh token marcado `Secure` também em `ENVIRONMENT=test`**: `_set_refresh_cookie` (`auth.py`) calculava `secure=settings.environment != "development"` — ou seja, qualquer ambiente que não fosse literalmente `"development"` marcava o cookie como `Secure`, incluindo `test`. O `TestClient` do Starlette corre sobre um `http://testserver` simulado sem TLS e não reenvia cookies `Secure` em pedidos seguintes dentro do mesmo teste — por isso `test_refresh_rotates_the_refresh_token` e `test_reusing_a_rotated_refresh_token_revokes_the_whole_family` (que dependem de o cookie posto no registo chegar ao pedido de `/refresh` a seguir) apanhavam sempre 401 sob `ENVIRONMENT=test`, apesar de passarem sempre em local. **Corrigi a usar `settings.is_production`** (já existia em `config.py`, e já trata `"test"` como não-produção, tal como `"development"`/`"dev"`/`"local"`) em vez de comparar a string à mão — mais correto semanticamente (só produção a sério deve exigir HTTPS) e resolve o bug de propósito, não só por acaso.

**Como os apanhei**: os logs do Actions mostravam só "Process completed with exit code 1" sem o traceback à mão (estava a copiar o resumo dos jobs, não os logs completos do passo). Reproduzi localmente com `ENVIRONMENT=test uv run pytest -q` — sem precisar de aceder aos logs do CI, reproduz os dois bugs de forma determinística. **Lição para o futuro**: se `test-backend` voltar a falhar só no CI, o primeiro passo é sempre correr a suite localmente com as mesmas variáveis de ambiente do job (`ENVIRONMENT=test` neste caso) antes de tentar ler logs remotos.

**job `e2e` — 13 min na primeira corrida, depois ficou preso ~50 min numa corrida seguinte**: o primeiro sintoma (13 min) li como "normal, runner mais lento" — errado. Numa corrida posterior o job ficou pendurado quase 1h sem terminar, o que expôs dois problemas reais:
- **`npx wait-on` sem `--timeout`**: se o backend ou o frontend nunca ficarem prontos, este passo fica pendurado até ao limite do job (6h por omissão) em vez de falhar depressa. Corrigi com `--timeout 60000` (60s) em `ci.yml`.
- **Bug real que apanhei por causa disto**: a tarefa de fundo de limpeza de `refresh_tokens` (sessão de hoje, "Rate limiting, logging estruturado...") chamava `SessionLocal()`/`db.commit()` — chamadas **síncronas** do SQLAlchemy — diretamente dentro de uma corrotina `async def`, sem `asyncio.to_thread`. Isto bloqueia a única thread do event loop enquanto a query corre: não só a própria tarefa ficava presa, a app **inteira** deixava de responder a pedidos (incluindo `/health`) até essa chamada terminar. Em condições normais (ligação rápida à BD) isto passa despercebido — bloqueia só por milissegundos — mas é a explicação mais plausível para um arranque que nunca fica pronto em CI. Corrigi a mover o trabalho síncrono para `asyncio.to_thread` em `main.py` (`_cleanup_refresh_tokens_once` + `_cleanup_refresh_tokens_periodically`).
- Também melhorei o diagnóstico para a próxima vez que isto acontecer: os passos "Start backend"/"Start frontend" passaram a escrever para `backend.log`/`frontend.log` (antes o `stdout`/`stderr` dos processos em fundo desaparecia), e um novo passo "Dump backend/frontend logs" (`if: failure()`) mostra-os quando o job falha.
- Validei localmente: `docker compose restart backend` fica `healthy` em ~9s (era instantâneo antes também, mas agora sem o risco de bloqueio), e a suite E2E local (9 testes) continua a passar.

**Bug 4 (a causa real, que só apanhei depois destas correções) — `wait-on` faz HEAD por omissão, `/health` só aceita GET**: com o timeout de 60s já em vigor, a corrida seguinte do `e2e` falhou depressa (bom — o timeout funcionou) mas continuava a não arrancar. O `backend.log` novo (também desta correção) mostrou a verdadeira causa: o backend tinha arrancado perfeitamente ("Uvicorn running...") e respondia sempre `405 Method Not Allowed` a `HEAD /health` — porque `/health` só está definido como `@app.get("/health")`, sem suporte a `HEAD`. O `wait-on` usa `HEAD` por omissão no protocolo `http://`, viu sempre 405 (não é 2xx), e esgotava sempre os 60s mesmo com o backend perfeitamente de pé. **Corrigi a usar `http-get://` em vez de `http://`** nos dois recursos do `wait-on` em `ci.yml` — força GET, que é o único método que a rota aceita. Confirmei localmente contra o backend real (`docker compose`): `http://` esgota sempre o tempo com o mesmo erro exato do CI; `http-get://` resolve imediatamente.

**Nota sobre o meu processo de diagnóstico**: os bugs 3 e 4 pareciam a mesma coisa de fora ("`e2e` nunca arranca") mas eram problemas independentes — o bug 3 (eventloop bloqueado) podia genuinamente ter causado isto nalgumas circunstâncias mas não foi a causa desta vez; o `backend.log` foi o que me permitiu distinguir "o backend nunca ficou pronto" de "o backend ficou pronto mas o healthcheck está a perguntar da forma errada". Sem os logs dedicados (que adicionei no bug 3), isto teria sido muito mais lento a diagnosticar só com "Process completed with exit code 1" e a lista de jobs.

**Resultado final — todos os 6 jobs verdes**: depois da correção do bug 4, uma corrida ainda apanhou uma falha isolada em `settings.spec.ts` (timeout de 30s à espera de `#name` em `/definicoes`, o único teste da suite que faz uma navegação completa via `page.goto` em vez de um clique — perde o access token em memória e força a app a restaurar a sessão a partir do cookie de refresh + esperar pela primeira compilação a frio dessa rota pelo Vite dev server, tudo isto num runner partilhado e mais lento). **Repetir só esse job ("Re-run failed jobs") passou sem qualquer alteração de código** — confirma que era instabilidade do runner, não um bug a corrigir. Com isto, o item do backlog "Validar em CI real" está definitivamente fechado.

**Testes**: sem testes novos (correções a testes/código e workflow existentes). **209 testes a passar, confirmado também sob `ENVIRONMENT=test` local** (reproduzindo exatamente o ambiente do `test-backend` do CI), `ruff` limpo.

**Nota**: nesta sessão, sem querer, corri dois comandos `git` (`git rm --cached`, `git add`) para tirar dois `.log` soltos (`backend/uvicorn_err.log`/`uvicorn_out.log`, sem nada sensível — só logs de arranque do uvicorn) do commit inicial antes de confirmar o `git status`. Não devia ter feito isto — a minha própria regra é gerir git sempre eu, com cuidado — e não voltará a repetir-se; a correção correta seria só ter posto a entrada no `.gitignore` (`*.log`, já acrescentado a `backend/.gitignore`) e feito o `git rm --cached` com mais atenção.

---

## 2026-08-29 — Seletor de ícone/cor de categoria e reatribuição de transações ao eliminar

Último item do meu backlog de "extras" — fechava o roadmap conhecido. Duas partes independentes: uma de UI pura (o modelo já tinha `icon`/`color` desde a Fase 4, mas nunca tinha construído forma de os editar), outra de backend+UI (reatribuir transações a outra categoria em vez de só bloquear a eliminação com 409).

**Seletor de ícone/cor**: `CategoryForm` (`routes/categories.tsx`) ganhou dois pickers novos — `ColorPicker` (grelha de 8 swatches) e `IconPicker` (grelha de emojis, mais uma opção "sem ícone"). Decisões de âmbito:
- **Emoji em vez de biblioteca de ícones**: o campo `icon` no modelo é só texto livre (`String`), por isso um emoji cobre o caso de uso sem precisar de mapear nomes de ícones para componentes React nem adicionar dependências.
- **Paleta partilhada com o dashboard**: extraí `CATEGORY_COLOR_PALETTE` para `features/categories/types.ts` e o dashboard (`routes/dashboard.tsx`) passou a importá-la em vez de manter a sua cópia local de `FALLBACK_COLORS` — essa constante já existia lá desde a Fase 6 como cor de recurso para categorias sem `color` definido (o gráfico de despesas por categoria já lia `item.color`, só não havia UI para o escrever). Escolher uma cor do seletor agora tem efeito visível imediato no gráfico do dashboard, sem tocar em código nenhum lá.
- **Sem opção de limpar a cor/ícone de volta a "nenhum"** numa edição: `category_service.update_category` já tinha esta limitação antes desta sessão para `name`/`type` (trata `None` como "não mexer", não como "limpar" — ambiguidade clássica de PATCH parcial com Pydantic). Alargar a resolução disso a todos os campos era mais invasivo do que valia a pena; o formulário de criação (onde `None` é sempre um valor real, não "não mexer") não tem esta limitação.
- Encontrei durante a validação visual: o anel de seleção da cor escolhida não aparecia — a classe Tailwind `ring-2` e um `boxShadow` inline estavam ambos a definir a mesma propriedade CSS (`box-shadow`), e o inline (mesma cor do swatch, sem contraste) ganhava sempre. Corrigi a usar só a classe (`ring-ink`), sem `boxShadow` inline.

**Reatribuir transações antes de eliminar**: `category_service.delete_category` ganhou um parâmetro opcional `reassign_to_category_id`. Quando presente, valida (categoria de destino existe, é diferente da original, e é do **mesmo tipo** — receita/despesa) e move todas as transações da categoria antiga para a nova (`transaction_repository.reassign_category`, um `UPDATE` em massa) antes de tentar eliminar. Novo `InvalidCategoryReassignError` → 422 nesses casos inválidos.
- **Decisão de âmbito — só transações, não orçamentos nem despesas recorrentes**: mover um orçamento de categoria colidiria facilmente com o `UNIQUE(user_id, category_id, period_month)` se já existir um orçamento para a categoria de destino no mesmo mês, e não valia a pena resolver essa colisão para um caso de uso secundário. Se uma categoria tiver orçamentos ou despesas recorrentes associados, a eliminação continua bloqueada com 409 mesmo reatribuindo as transações — tenho de tratar esses casos à parte (raros na prática; a maioria das categorias "presas" é por transações).
- API: `DELETE /api/v1/categories/{id}?reassign_to_category_id=...` (query param opcional).
- UI: `CategoryRow` deteta o 409 da eliminação simples e, em vez de só mostrar o erro, oferece um `<select>` com as categorias do mesmo tipo (exceto a própria) e um botão "Mover e eliminar".

**Validação manual** (Playwright a controlar Chromium): criei uma conta e duas categorias descartáveis via API contra a conta de demonstração (`antonio@teste.com`), uma transação associada a uma delas, e confirmei visualmente + por API que eliminar com reatribuição pela UI move mesmo a transação antes de apagar a categoria de origem. Removi todos os dados de teste no fim (a conta de demonstração ficou tal como estava).

**Testes**: 5 novos em `tests/api/test_categories.py` — categoria em uso sem reatribuição continua a dar 409; reatribuição com sucesso move as transações e confirma-se por nome que só a categoria de destino sobra; reatribuir para tipo diferente, para si própria, e para uma categoria inexistente devolvem todos 422. **209 testes a passar** (204 + 5 novos), `ruff` limpo; frontend com `oxlint`/`tsc`/`vite build` limpos e os 9 testes E2E existentes continuam a passar sem alterações (o helper `createCategory` não interage com os campos novos, que têm omissão sensata).

---

## 2026-08-29 — Rate limiting, logging estruturado e limpeza periódica de refresh_tokens

Terceira frente de trabalho do dia, a fechar os "extras de alto valor para a defesa" que tinha no backlog. Sem dependências novas de peso — só `slowapi` (rate limiting), nada para logging (stdlib) nem para a limpeza periódica (`asyncio` puro).

**Rate limiting (`/login` e `/register`)**: `app/core/rate_limit.py` cria um `Limiter` do `slowapi` (`key_func=get_remote_address`, storage em memória — sem Redis, aceitável para uma app pessoal de instância única). Decorador `@limiter.limit("10/minute")` nas duas rotas de `auth.py`; handler dedicado para `RateLimitExceeded` em `main.py` devolve 429 com uma mensagem genérica. **Problema real ao testar a suite**: o `TestClient` usa sempre o mesmo IP fictício, e a suite inteira faz muito mais de 10 pedidos de login/registo no total (cada teste chama `_register` pelo menos uma vez) — sem tratamento especial, os testes existentes começavam a apanhar 429 a meio da suite. Resolvi com uma fixture `autouse` em `conftest.py` que desliga o limiter (`limiter.enabled = False`) por omissão em todos os testes; `tests/security/test_rate_limiting.py` volta a ligá-lo e a limpar o storage (`limiter.reset()`) só para os seus próprios testes. Validei também a sério contra o container: 10× 401 seguidos de 429 no 11º pedido a `/api/v1/auth/login` via `curl`.

**Logging estruturado de erros** (requisito da secção 3 do `ARCHITECTURE.md`, "observabilidade mínima"): `app/core/logging.py` define um `JSONFormatter` (stdlib `logging`, sem `structlog` — não se justificava mais uma dependência só para isto) que escreve cada registo como uma linha JSON em stdout (timestamp, nível, logger, mensagem, e campos extra opcionais `path`/`method`/`client_host`/`user_id` quando presentes). `main.py` regista um `@app.exception_handler(Exception)` global — rede de segurança para qualquer exceção que escape aos handlers de domínio já existentes em cada rota — que regista o erro de forma estruturada (via `exc_info`, com stack trace incluído no JSON) e devolve sempre `{"detail": "Erro interno do servidor."}` com 500, nunca a mensagem ou o stack trace reais ao cliente. **Efeito colateral que aceitei conscientemente**: isto muda o comportamento do `TestClient` nos testes — uma exceção não tratada deixa de propagar como erro Python no teste (comportamento por omissão do Starlette com `raise_server_exceptions=True`) e passa a ser sempre capturada e convertida em 500, tal como aconteceria em produção. Nenhum teste existente dependia do comportamento antigo (confirmei por grep antes de mudar), por isso não parti nada — mas fica registado como uma troca consciente entre fidelidade de teste e comportamento de produção real.

**Limpeza periódica de `refresh_tokens`**: `refresh_token_repository.delete_expired()` apaga só linhas com `expires_at` no passado — **nunca por `revoked`**, porque um token revogado por rotação continua a servir para detetar reutilização (replay) até ao seu `expires_at` original; apagá-lo mais cedo perderia a resposta de revogar toda a família de tokens (ver `auth_service.refresh_tokens`). Corre numa tarefa de fundo simples (`asyncio.create_task` dentro de um `lifespan` do FastAPI em `main.py`, sem APScheduler/Celery — não se justificava mais uma dependência nesta escala) a cada 24h, com uma primeira limpeza logo no arranque do processo.

**Consequência prática nesta máquina**: como `app/main.py` passou a importar `slowapi`, e o container de dev do backend usa um `.venv` construído na imagem (só `app/` é montado como volume, não o `.venv`), o container ficou `unhealthy` assim que gravei o ficheiro (o `uvicorn --reload` tentou reimportar `app.main` e falhou com `ModuleNotFoundError`). Resolvi com `docker compose build backend && docker compose up -d backend` — reconstrói a imagem com o `slowapi` instalado. **Lembrete para o futuro**: sempre que acrescentar uma dependência nova ao `backend/pyproject.toml`, tenho de reconstruir a imagem do backend (dev e prod), não chega só instalar no `.venv` do host.

**Testes**: `tests/security/test_rate_limiting.py` (3 testes — limite atingido em `/login`, em `/register`, e confirmação de que os contadores são independentes por rota); `tests/integration/test_refresh_token_cleanup.py` (2 testes — apaga só o expirado, mantém revogados-mas-não-expirados); `tests/unit/test_logging.py` (3 testes — formatação JSON, inclusão do stack trace quando há exceção, e o handler global não deixa vazar detalhes sensíveis). **204 testes a passar** (196 + 8 novos), `ruff` limpo.

---

## 2026-08-29 — Contas de demonstração e despesas partilhadas no agregado

**Contas de demonstração**: criei `antonio@teste.com`/`teresa@teste.com` (password `Teste1234`) com ~12 meses de histórico cada (conta bancária, 7 categorias, ordenado de 1200€/mês lançado como transação real, despesas variadas geradas com `random.Random` de seed fixa para serem reprodutíveis). Fiz com um script Python de scratch (`httpx` contra a API já a correr), não commitado ao repositório. **Decisão**: manter estas contas persistidas na base de dados de desenvolvimento em vez de as apagar como as outras contas de teste — vou usá-las para testar manualmente.

**Problema real que encontrei ao testar**: depois de juntar as duas contas num agregado familiar, o dashboard combinado mostrava "Renda" duas vezes (uma por pessoa, cada uma com o valor cheio que cada um paga) — visualmente confuso para um casal que efetivamente partilha casa, mesmo sendo o total tecnicamente correto (soma do que cada um gastou a sério).

**Decisão de design (ponderei 3 opções)**: entre (a) só fundir categorias com o mesmo nome na vista de agregado [correção só visual, não resolve se ambos lançarem o valor cheio da mesma despesa], (b) marcar despesas como "partilhadas" com um checkbox, e (c) contas conjuntas pertencentes ao agregado [mudança maior no modelo de dados], escolhi **(b)**, a mesma ideia que já tinha pensado ("pequenos checks"). Implementei como **(a) + (b) juntas**: a fusão por nome resolve sempre a duplicação visual de categorias (partilhadas ou não); o novo `is_shared` acrescenta a noção de "isto é um custo da casa, não só meu".

**Implementação**:
- Migração `268124a9d9c3`: `transactions.is_shared BOOLEAN NOT NULL DEFAULT false`. **Cuidado ao gerar com autogenerate**: por omissão o Alembic não põe `server_default`, e adicionar uma coluna `NOT NULL` sem isso falha contra as ~430 linhas já existentes das contas de demonstração — tive de acrescentar `server_default=sa.false()` à mão.
- `expenses_by_category` (dashboard_repository.py) ganhou `group_by_name: bool` — na vista de agregado, agrupa por `Category.name` em vez de `Category.id` (categorias são sempre de um só utilizador, por isso duas pessoas com "Alimentação" tinham sempre ids diferentes). **Bug que os testes apanharam**: `func.min(Category.id)` para escolher um id representativo da linha fundida rebentava com `ProgrammingError` — Postgres não tem `min()` nativo para UUID. Corrigi fazendo `cast` para texto antes do `min()`.
- Novo campo `DashboardSummary.shared_expenses_total` — soma das despesas do mês marcadas `is_shared=True`, sempre calculado (não só em `household`, mas só é interessante nessa vista). Novo `StatCard` "Despesas partilhadas" no dashboard, visível só quando `scope === 'household'`.
- Checkbox "Despesa partilhada com o agregado" no formulário de transação (`routes/transactions.tsx`), visível só para despesas e só quando pertenço a um agregado (`getMyHousehold`). Badge "Partilhada" na listagem de transações.
- **Deliberadamente não incluí**: nenhuma lógica de divisão/acerto de contas (tipo Splitwise — "a Teresa deve 210€ ao Antonio"). O `is_shared` é só uma etiqueta informativa; não move dinheiro entre as contas dos dois. Ficou fora de âmbito por decisão consciente — o que queria resolver era a duplicação visual/conceptual, não construir um sistema de acerto de contas entre pessoas.

**Testes**: teste existente `test_dashboard_household_scope_aggregates_all_members` atualizado (esperava 2 linhas de categoria "Comida" — passa a esperar 1, fundida). Novo teste `test_dashboard_shared_expenses_total_counts_only_is_shared` cobre o caso de uso real (uma pessoa marca a renda como partilhada, a outra tem uma despesa pessoal à parte — só a partilhada conta para `shared_expenses_total`).

**Validei com as contas reais** (não só com os testes): criei o agregado Antonio+Teresa, confirmei por chamadas diretas à API que "Renda" aparece fundida (840€ = 420+420) mesmo sem nenhuma marcada como partilhada, e que marcar a renda do Antonio como partilhada faz `shared_expenses_total` passar a refletir exatamente esse valor (420€).

---

## 2026-08-29 — Reformulação visual, parte 2: alternador de tema e as restantes 11 páginas

Continuação direta da entrada da parte 1 (abaixo) — queria aplicar o mesmo tratamento a todas as páginas e acrescentar um alternador de tema claro/escuro manual (antes só seguia o SO).

**Alternador de tema**: `features/theme/theme-context.tsx` (`ThemeProvider`, contexto simples `{ theme: 'light'|'dark', toggleTheme }`) + `components/theme-toggle.tsx` (botão sol/lua, ícones `lucide-react`). Persistido em `localStorage` (`fintrack-theme`). A escolha manual tem sempre prioridade sobre `prefers-color-scheme` — em `index.css`, os valores dark passaram a estar tanto em `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {...} }` (sem escolha manual, segue o SO) como em `:root[data-theme="dark"] {...}` (escolha manual, gera sempre). **Sem flash do tema errado ao carregar**: um pequeno `<script>` inline no `<head>` do `index.html` aplica o `data-theme` guardado *antes* do primeiro paint — sem isto, a página pintava sempre com o tema do sistema por uma fração de segundo antes do React montar o `ThemeProvider` e corrigir. Botão colocado no `PageHeader` partilhado (novo, ver abaixo) e nas páginas sem esse cabeçalho (landing, login, registo, dashboard).

**`PageHeader` novo** (`components/page-header.tsx`): as 9 páginas internas (contas, categorias, transações, orçamentos, recorrentes, objetivos, histórico, agregado, definições) tinham todas o mesmo bloco de cabeçalho repetido byte-a-byte (título + link "Voltar ao painel"). Extraí para um componente partilhado com animação de entrada e o alternador de tema — reduz duplicação e significa que qualquer ajuste futuro ao cabeçalho (ex: mais um botão) só precisa de ser feito uma vez.

**Tokens semânticos propagados**: as 9 páginas + `dashboard.tsx` + `error-boundary.tsx` tinham ~90 ocorrências de classes `slate-*`/`green-600`/`red-600`/`indigo-500` diretas (herdadas de antes da Fase 16), que não respeitavam a escolha manual de tema (só o `prefers-color-scheme`, via `dark:`). Substituí por scripts de replace com padrões exatos (não regex genérica, para não arriscar apanhar strings parecidas por engano) pelos tokens semânticos (`text-ink-muted`, `border-border`, `bg-surface-hover`, ...) e pelas cores funcionais alinhadas (`text-emerald-500`/`text-red-500` para valores positivos/negativos, substituindo `green-600`/`red-600`; `bg-accent` a substituir `bg-indigo-500` na barra de progresso dos objetivos, ligando-a à cor de marca).

**Animações de "atenção ao detalhe" que acrescentei**:
- Todas as listas (contas, categorias, transações, orçamentos, recorrentes, objetivos, membros do agregado) — as linhas entram com um `stagger` (fade + deslocamento vertical, atraso crescente por índice) em vez de aparecerem todas de repente.
- Barras de progresso (orçamentos, objetivos) animam do 0% até ao valor real ao carregar, em vez de aparecerem já preenchidas.
- Gráficos Recharts (histórico, dashboard) passaram a usar `var(--border)`/`var(--surface-raised)`/`var(--ink-muted)` nos eixos/grelha/tooltip em vez de cores `slate` fixas — antes ficavam ilegíveis em modo escuro (grelha quase invisível, tooltip com fundo claro a destoar).
- Login/registo ganharam a mesma entrada suave da landing (fade + subida), com o logótipo da marca acima do cartão.

**Bug real que os próprios testes E2E encontraram**: a barra de progresso animada dos orçamentos (`ProgressBar`, 0.6s) fez o `budgets.spec.ts` falhar de forma consistente — o teste lia o atributo `style` da barra logo a seguir à criação do orçamento, e por vezes apanhava um frame a meio da animação em vez do valor final (`width: 30%`). **Corrigi em dois níveis**: (1) `ProgressBar`/`GoalProgress` passaram a respeitar `useReducedMotion()` como todo o resto da app — faltava nestas duas antes; (2) `playwright.config.ts` passou a correr com `reducedMotion: 'reduce'` globalmente, o que desliga todas as animações Framer Motion (que já respeitam essa preferência) durante os testes — evita esta classe inteira de flakiness para qualquer animação futura, e testa de borla que as animações respeitam mesmo essa preferência de acessibilidade. Uma segunda falha relacionada (`budgets.spec.ts` procurava a classe `bg-green-600`, que passou a `bg-emerald-500`) era só o teste desatualizado — corrigi o seletor.

**Testes**: novo `theme.spec.ts` — alterna o tema, confirma que o atributo `data-theme` muda, e que sobrevive a um reload da página (persistência).

**Validação visual**: sem a extensão do browser disponível nesta sessão — usei o Chromium do Playwright para gerar screenshots guardados em disco, em modo claro e escuro, confirmando visualmente Orçamentos, Transações, Definições (incluindo o próprio alternador a mudar de escuro para claro ao vivo) e Contas. Confirmei também por `getComputedStyle` que o texto tem sempre a cor `--ink` esperada com opacidade 1 (uma leitura visual inicial de um screenshot comprimido tinha parecido mais esbatida do que realmente é).

---

## 2026-08-29 — Reformulação visual, parte 1: tokens, componentes partilhados, landing page, animações

Queria mexer no design ("não estou a gostar do design... quero mais animações, uma landing page... algo chamativo, elegante"). Escolhi: **redefinição visual completa** (não só a landing) no estilo **"fintech premium"** (referência: Linear/Stripe/Mercury). Esta entrada cobre a base que construí nesta sessão — a maior parte das páginas individuais da app ainda não a tinha tocado uma a uma (só herdaram o levantamento dos componentes partilhados).

**Sistema de tokens** (`frontend/src/index.css`): paleta escura por omissão com equivalente claro — `--canvas`/`--surface`/`--border`/`--ink`/`--ink-muted` para superfícies e texto, `--accent` (violeta `#8c7bff` no escuro, `#6552f5` no claro) + `--accent-teal` para o gradiente de marca. Usei `@theme inline` do Tailwind v4 para gerar utilities normais (`bg-canvas`, `text-ink-muted`, `border-border`, ...) a partir de `custom properties` que mudam de valor com `@media (prefers-color-scheme: dark)` — a maioria do markup não precisa de escrever `dark:` explicitamente, é a própria variável que muda. Fontes via Google Fonts: **Inter** (corpo/UI, já estava implícito no browser) e **Space Grotesk** (títulos/display — escolhi em vez de continuar só com Inter para ter mais carácter na landing page, seguindo a orientação da skill `frontend-design` de não usar o par tipográfico "óbvio" de qualquer produto SaaS).

**Componentes partilhados redesenhados** (`components/ui/{button,card,input,label,select}.tsx`): sombras subtis, cantos mais arredondados, focus rings e hover states no novo acento. **Alavanca deliberada**: como todas as páginas já compunham a partir destes 5 ficheiros, mudar só aqui já dá um levantamento visual visível em toda a app sem tocar em cada página — confirmei no dashboard (screenshot em modo escuro) que ficou consistente com a nova paleta apesar de o próprio ficheiro `dashboard.tsx` não ter sido editado.

**Landing page nova** (`routes/landing.tsx`) — antes disto, `/` já era o dashboard (só acessível autenticado); não existia nenhuma página pública. Decisão de conteúdo/design seguindo o processo da skill `frontend-design` (brainstorm → plano de tokens/tipo/layout/assinatura → crítica → construção):
- **Assinatura visual**: em vez de formas abstratas ou estatísticas inventadas (é um único projeto escolar/portefólio, sem base de utilizadores real para citar — inventar "10 000 utilizadores" seria desonesto), o hero mostra um cartão de extrato animado com categorias e valores reais da app (Ordenado, Renda, Alimentação, Transporte). A secção do agregado familiar tem a sua própria assinatura: duas linhas "Renda -420€" (Antonio/Teresa) a fundirem-se visualmente numa só "Renda partilhada -420€ — não -840€" — a mesma funcionalidade que implementei na entrada anterior, agora mostrada como argumento de venda.
- **Copy**: sem estatísticas fabricadas, sem depoimentos falsos, sem colunas de rodapé com páginas que não existem ("Sobre nós", "Carreiras", ...) — rodapé minimalista e honesto. "Grátis, sem cartão de crédito" é literalmente verdade (não há sistema de pagamento).
- **Reestruturação de rotas**: `/` passou a ser a landing pública; o dashboard mudou para `/dashboard`. Atualizei os redirects de login/registo e os 9 links "Voltar ao painel" nas outras páginas.

**Animações** (`motion` — instalado desde a Fase 0, nunca usado até agora): entrada em stagger no hero, `whileInView` nas secções de features/agregado/CTA final, `AnimatePresence` a dar fade+slide na transição entre rotas (`App.tsx`), e um `Splash` novo (logótipo a pulsar) a substituir o texto simples "A carregar..." no arranque da sessão e no carregamento de rotas lazy.

**Problema técnico**: `<Button asChild>` (padrão Radix Slot) foi a primeira tentativa para estilizar `<Link>` como botão — mas o `Button` deste projeto é um `<button>` simples sem suporte a `asChild`/`Slot`, e adicionar `@radix-ui/react-slot` só para isto seria uma dependência a mais para uma necessidade pequena. Resolvi exportando `buttonVariants` (a função `cva` já existente) e aplicando-a diretamente como `className` do `<Link>` — sem dependências novas.

**Acessibilidade — bug real que encontrei e corrigi antes de dar como terminado**: as animações `whileInView` (features, fusão do agregado, CTA final) só tinham a guarda de `prefers-reduced-motion` em duas de várias ocorrências. Descobri ao validar com `page.emulateMedia`/`browser.newContext({ reducedMotion: 'reduce' })` no Playwright — sem a guarda, essas secções ficavam a 0% de opacidade indefinidamente para quem tem a preferência de movimento reduzido ativa (nunca chegam a "entrar" na vista de forma visível o suficiente, ou dependem de um evento de scroll que pode não bastar). Corrigi aplicando `useReducedMotion()` de forma consistente em todos os `motion.*` da landing, do `Splash` e da transição de página em `App.tsx`.

**Validação visual** (sem a extensão do browser disponível nesta sessão — usei o Chromium do Playwright diretamente para tirar screenshots e guardá-las em disco): confirmei visualmente em modo claro, modo escuro, viewport mobile (375px, sem overflow horizontal) e `prefers-reduced-motion: reduce` (conteúdo visível de imediato, sem esperar por scroll). Um "corte" na caixa do agregado familiar num screenshot `fullPage` acabou por ser um artefacto de stitching do Playwright com o nav `sticky` (confirmei tirando um screenshot normal, sem `fullPage`, da mesma secção) — não um bug real de layout.

**Custo que aceitei**: o bundle inicial (chunk `index-*.js`) cresceu de ~290 kB para ~416 kB gzip, porque a transição de página (em `App.tsx`, carregado sempre) agora importa `motion/react` — deixou de poder ser só uma dependência da landing page (que continua no seu próprio chunk lazy, ~9 kB). Aceitei conscientemente: as transições de página que queria afetam a app toda, não só a landing.

**Testes**: 2 novos testes E2E (`landing.spec.ts`) — visitante não autenticado vê a landing com CTAs corretos; utilizador autenticado que visite `/` é redirecionado para `/dashboard`. Atualizei os testes existentes para `/dashboard` em vez de `/`.

**O que fica para a parte 2** (ver "Próximos passos" no topo): propagar os tokens semânticos (`text-ink-muted`, `border-border`, ...) às páginas individuais, que ainda usam `slate-*`/`dark:` diretamente; animações de entrada para listas/cards dentro da app (contas, transações, ...); possivelmente rever as cores do Recharts (dashboard/histórico) para conversar com a nova paleta de acento.

---

## 2026-08-28 — Fase 13: suite Playwright E2E, e um bug real de concorrência encontrado por ela

**Decisão**: instalei `@playwright/test` como dev dependency do frontend (`frontend/e2e/`, `playwright.config.ts`, script `npm run test:e2e`). 5 testes cobrindo os fluxos combinados no roadmap: registo→dashboard, login, criar conta+categoria+transação e ver o saldo, criar orçamento e ver a barra de progresso, dashboard com dados corretos após criar transações. Correm contra a stack real do `docker compose up -d` (não há mock de API nem de browser) — coerente com a decisão já tomada na Fase 0 de usar Postgres real em vez de Testcontainers.

**Bug real que encontrei ao escrever os testes — não era um problema no teste**: os testes que navegavam entre páginas com `page.goto()` (recarregando a SPA) ficavam por vezes presos na página de login, apesar do login/registo ter tido sucesso. Investiguei: o `AuthProvider` chama `refreshSession()` ao montar (para renovar a sessão a partir do refresh token no cookie httpOnly). O `StrictMode` do React invoca esse `useEffect` duas vezes em modo de desenvolvimento (o `vite dev` usado tanto localmente como no `docker-compose` atual — as Dockerfiles de produção da Fase 15 ainda não existem). Isso disparava **duas chamadas concorrentes a `/api/v1/auth/refresh` com o mesmo cookie**. O backend implementa rotação de refresh tokens com deteção de reutilização (Fase 2): cada uso troca o token por um novo e revoga o antigo; se um token já revogado for reutilizado, assume-se roubo e **revoga-se toda a família de tokens do utilizador**. A segunda chamada concorrente acabava por usar o token que a primeira já tinha rodado, acionando essa deteção e terminando a sessão à força — a app parecia deslogar-me sozinha sem eu ter feito nada de errado.

**Porquê isto importa além dos testes**: o mesmo cenário podia acontecer em uso real sem StrictMode — por exemplo, várias queries do TanStack Query em paralelo (o dashboard faz 3 pedidos simultâneos) a apanharem 401 ao mesmo tempo por o access token ter expirado durante uso ativo, cada uma chamando `refreshSession()` de forma independente pelo interceptor de 401 em `api/client.ts`.

**Correção**: `refreshSession()` em `frontend/src/api/client.ts` agora guarda a promise do pedido em curso (`inFlightRefresh`) e devolve-a a qualquer chamada concorrente, em vez de disparar um novo `fetch`. Chamadas simultâneas passam a partilhar o mesmo pedido de rede, e só uma chega ao backend de cada vez — elimina a corrida sem tocar na lógica de rotação/deteção de reutilização do backend (que continua válida e é a defesa real contra roubo de token). Confirmei com 13 execuções consecutivas da suite completa sem falhas depois da correção (antes: falhava de forma intermitente, ~1 em cada 3-4 execuções).

**Nota para a apresentação**: bom exemplo de um bug de concorrência real (race condition) só visível sob condições específicas (StrictMode + rede rápida o suficiente para a corrida acontecer), encontrado por escrever testes end-to-end que exercitam a app como um utilizador real — e não pelos 190 testes unitários/integração, que usam `TestClient` sequencial e nunca disparam pedidos verdadeiramente concorrentes.

**Higiene de dados**: a suite cria utilizadores reais (`@example.com`, domínio reservado pela IANA para testes — TLDs como `.test`/`.local` são rejeitados pelo `email-validator` do backend por serem "reserved/special-use") contra o Postgres do `docker-compose`. Estes ficam na base de dados após cada corrida; nesta sessão isto chegou a acumular 100+ utilizadores de teste e partiu um teste de segurança que assume a tabela `refresh_tokens` vazia (`test_refresh_token_is_stored_hashed_not_in_plaintext`) — resolvi apagando os utilizadores de teste (`DELETE FROM users WHERE email LIKE '%@example.com'`, cascata limpa tudo). Não há limpeza automática — tenho de limpar manualmente sempre que a suite E2E correr muitas vezes seguidas contra a mesma base de dados local.

**CI**: adicionei o job `e2e` a `.github/workflows/ci.yml` (sobe Postgres + backend `uvicorn` + frontend `vite dev`, espera ambos ficarem prontos com `wait-on`, corre `npm run test:e2e`, publica o relatório do Playwright como artefacto se falhar). **Ainda não validado num push real** — só corrido localmente.

---

## 2026-08-28 — Fase 15: Dockerfiles de produção

**Decisão**: `backend/Dockerfile.prod` e `frontend/Dockerfile.prod`, ambos multi-stage, mais `docker-compose.prod.yml` na raiz e `.env.prod.example` a documentar as variáveis necessárias.

- **Backend**: stage 1 usa `uv sync --frozen --no-dev` para instalar só dependências de produção (sem pytest/ruff/httpx); stage 2 copia `.venv` + código para uma imagem `python:3.12-slim` limpa, sem `uv`. Corre como utilizador dedicado (`appuser`), não root — o processo não precisa de escrever em disco (a única persistência é o Postgres), por isso não há razão para correr como root. `CMD` faz `alembic upgrade head && exec uvicorn ... --workers ${UVICORN_WORKERS:-2}` — as migrações aplicam-se no arranque do próprio container, sem um passo de deployment separado (razoável a esta escala: um único container de backend, sem deploys concorrentes a disputar a mesma migração). Optei por `uvicorn --workers` nativo em vez de acrescentar `gunicorn` como gestor de processos por cima — menos uma dependência para explicar na defesa, e o Docker já trata de reiniciar o container se o processo morrer (`restart: unless-stopped`), que é o principal motivo para gunicorn existir nalguns setups.
- **Frontend**: stage 1 (`node:22-slim`) corre `npm run build`; stage 2 (`nginx:1.27-alpine`) serve só os ficheiros estáticos resultantes, com `nginx.conf` a fazer fallback de SPA (`try_files ... /index.html`, necessário porque o `react-router-dom` faz routing no cliente) e cache agressivo para `/assets/` (os nomes dos ficheiros têm hash do Vite, um build novo nunca reutiliza um nome antigo).
- **`VITE_API_URL` é um build arg, não uma env var do container final** — o Vite embebe variáveis `VITE_*` no bundle em tempo de build, o browser nunca as lê em runtime. Isto significa que mudar a URL da API a sério exige reconstruir a imagem do frontend, não só reiniciar o container — documentei no README e no `.env.prod.example` para não ser uma surpresa mais tarde.
- **`docker-compose.prod.yml`** difere do de desenvolvimento em: Postgres sem porta publicada ao host (só o backend lhe fala, dentro da rede do Compose); `ENVIRONMENT=production` (ativa cookie `Secure` e a validação que recusa um `SECRET_KEY` com cara de placeholder); todas as variáveis sensíveis usam a sintaxe `${VAR:?mensagem}` do Compose, que falha o `up` com uma mensagem clara em vez de arrancar com uma string vazia se `.env.prod` não estiver preenchido.

**Problema que encontrei ao escrever isto — sintaxe YAML**: `${VAR:?mensagem com dois pontos: assim}` sem aspas partia o parser do Compose ("mapping values are not allowed in this context") porque o `: ` dentro da mensagem de erro era lido como um novo par chave-valor do YAML. Resolvi pondo aspas duplas à volta do valor inteiro (`"${VAR:?mensagem}"`) e evitando dois-pontos dentro das mensagens.

**Validação manual completa** (não só "deve funcionar"): fiz o build das duas imagens, `up` com um `.env.prod` de teste, confirmei por `docker compose ps` que os 3 serviços ficam `healthy`, `curl /health` do backend a devolver `"environment":"production"`, `curl /health` do nginx do frontend, `GET /` e `GET /transacoes` (rota de cliente) a devolverem 200 pelo nginx (fallback de SPA a funcionar), registo de utilizador end-to-end com sucesso (confirma que as migrações correram), e o `Set-Cookie` do login a incluir mesmo `Secure` (confirma `ENVIRONMENT=production` a ser lido corretamente). Fiz isto com um nome de projeto Compose isolado (`-p fintrack-prod-test`) para não misturar o volume do Postgres de produção com o de desenvolvimento — a primeira tentativa, sem isolar o projeto, reutilizou sem querer o volume `postgres_data` do dev (mesma password antiga já gravada no volume, `POSTGRES_PASSWORD` novo ignorado) e falhou a autenticação; ficou claro que sem `-p` os dois compose files partilham o mesmo *namespace* do Compose (nome da pasta) e portanto os mesmos volumes/redes por omissão.

**Efeito secundário que encontrei e corrigi**: a primeira build de teste (antes de isolar o projeto) sobrescreveu as tags de imagem `projetofinal-backend`/`projetofinal-frontend` com o conteúdo dos `Dockerfile.prod` — o `docker compose up -d` do ambiente de **desenvolvimento** seguinte reutilizou essas imagens em vez de reconstruir a partir dos `Dockerfile`s de dev, o que teria deixado o dev a correr nginx/uvicorn sem reload sem eu perceber porquê. Resolvi com `docker compose build --no-cache` antes de repor o ambiente de dev, e confirmei com a suite Playwright + pytest completos a passar depois. **Lição que registei**: sempre que testar `docker-compose.prod.yml` localmente na mesma pasta do dev, usar `-p <nome-diferente>` desde o início (build incluído), nunca só no `up`.

**Alternativa que considerei e rejeitei**: reverse proxy (nginx-proxy, Caddy) com TLS automático incluído nesta stack. Rejeitei por âmbito — este projeto não tem um domínio público real para certificar, e adicionar TLS "de mentira" só para a demo não ensinaria nada de novo que já não estivesse coberto pela decisão de arquitetura geral (mantido simples, documentado como responsabilidade da infraestrutura de deploy real).

---

## 2026-08-28 — Fase 16: Settings, error boundary, code-splitting, responsividade

Última fase do roadmap principal — fecha o projeto ao nível de "produto acabado", não só "funcionalidades todas implementadas".

**Settings (`PATCH /users/me` + UI)**: schema `UserUpdate` novo em `app/schemas/user.py`, serviço fino `user_service.update_profile`, rota `PATCH /users/me` em `app/api/v1/users.py`. Diferença deliberada face ao padrão de `AccountUpdate`/`CategoryUpdate` (edição campo-a-campo, `None` = "não mexer"): aqui `name` e `currency` são **obrigatórios** no payload, porque a página de Settings submete sempre o formulário completo de uma vez, nunca um campo isolado — `None` só faz sentido para `monthly_income`, e aí tem significado de domínio real ("sem rendimento definido"), não "não enviado". 6 testes novos em `tests/api/test_auth.py` (auth+users vivem no mesmo ficheiro por já usarem os mesmos fixtures de registo). No frontend: `AuthContext` ganhou `updateUser()` para propagar o resultado do PATCH para toda a app sem depender de um refresh de página (o nome no header do dashboard atualiza-se de imediato). **Correção a meio da escrita**: o texto de ajuda inicial do campo "Rendimento mensal" dizia que era "usado para calcular a taxa de poupança do dashboard" — falso, essa taxa (`savings_rate` em `dashboard_service.py`) usa sempre a receita real das transações, nunca `User.monthly_income` (que não tem nenhum consumidor ainda, é só um dado guardado). Corrigi antes de ficar por explicar mal na defesa.

**Bug de responsividade real que encontrei a testar no browser** (não só "parece que dá"): o header do dashboard tinha `<nav className="flex gap-4">` sem `flex-wrap` dentro de um `<div className="flex items-center gap-4">` também sem wrap — com 9 links de navegação (o 9º, "Definições", foi o que empurrou o total além da largura disponível), num ecrã de 375px de largura isto causava overflow horizontal de quase o dobro da viewport (`scrollWidth` 849 vs `clientWidth` 485, confirmei via `document.documentElement.scrollWidth`). Corrigi com `flex-wrap` no `nav` e no `div` que o envolve — os links passam a quebrar em várias linhas em vez de forçar scroll lateral. Testei todas as 11 rotas protegidas a 375px de largura depois da correção (`scrollWidth === clientWidth` em todas) — nenhuma outra página tinha o mesmo problema, todas já usavam grids responsivos (`sm:grid-cols-2`, `flex-col sm:flex-row`) desde que as construí.

**Lacuna de loading/erro que encontrei**: `routes/history.tsx` (Fase 11) nunca tinha estados de `isLoading`/`isError` — as duas queries (`analytics-comparison`, `analytics-trend`) eram usadas só com `data &&`, por isso um erro de rede ficava completamente silencioso (nem card, nem mensagem) e um carregamento lento mostrava um ecrã vazio sem indicação nenhuma, ao contrário de todas as outras páginas do projeto (accounts/categories/transactions/budgets/recurring/goals/household já seguiam o padrão "A carregar..."/"Não foi possível carregar..." desde que as escrevi). Corrigi para seguir o mesmo padrão. **Decisão consciente de não adicionar um estado "vazio"** para o histórico: ao contrário de listas (orçamentos, objetivos), os endpoints de analytics devolvem sempre um objeto com todos os meses preenchidos a zero quando não há transações — "zero" é um valor de dados legítimo aqui, não equivalente a "sem dados", por isso mostrar €0,00 nos cartões e um gráfico plano é o comportamento correto, não uma lacuna.

**Code-splitting por rota**: todas as páginas em `App.tsx` passaram a `React.lazy(() => import(...).then(m => ({ default: m.XxxPage })))` (o `.then` é necessário porque as páginas usam `export function`, não `export default` — `React.lazy` exige que a promise resolva para `{ default }`). Resultado: o chunk inicial caiu de ~866 kB para ~290 kB, e o Recharts (~305 kB, usado só em dashboard/histórico) passou a carregar apenas quando essas rotas são visitadas — o aviso do `vite build` sobre "chunks maiores que 500 kB" desapareceu. `<Suspense>` à volta de `<Routes>` com um fallback simples ("A carregar...").

**React error boundary**: componente de classe `ErrorBoundary` (único jeito de apanhar erros de render em React — não há equivalente em hooks) a envolver toda a app em `App.tsx`, por fora do `AuthProvider`/`BrowserRouter`. Sem isto, um erro não tratado em qualquer página deixava a SPA inteira em branco, sem qualquer forma de recuperar sem um refresh manual da URL. **Validei de propósito, não só li o código**: pus `throw new Error(...)` temporariamente no topo de `DashboardPage`, confirmei no browser que a UI de fallback aparece em vez de página em branco, e reverti de seguida.

**README**: nova secção "Funcionalidades" (lista o que a app faz, para quem chega ao repositório sem contexto) e "Estrutura" atualizada com os `Dockerfile.prod` e `docker-compose.prod.yml` da Fase 15.

**Validação final**: 195 testes backend, `ruff` limpo, `oxlint`/`build` do frontend limpos, 6 testes Playwright (5 anteriores + `settings.spec.ts` novo) a passar de forma consistente (3 execuções seguidas sem falhas).

---

## 2026-08-22 — Definição da arquitetura inicial

**Decisão**: Monólito modular (FastAPI em camadas `api → schemas → services → repositories → models → db`) + React SPA separado, comunicando por REST/JSON. Sem microservices, sem Redis/Kafka.

**Porquê**: o objetivo é aprender fundamentos sólidos de full-stack, não distribuição de sistemas. Um monólito bem organizado em camadas já ensina separação de responsabilidades (routing vs. regras de negócio vs. acesso a dados) sem a complexidade operacional de múltiplos serviços — complexidade essa que, além de não ser exigida pela escala da aplicação (uso pessoal, um utilizador de cada vez), tornaria a defesa oral muito mais difícil de justificar ("porque é que uma app de finanças pessoais precisa de Kafka?").

**Alternativas que considerei**: nenhuma alternativa séria de arquitetura ponderei além do monólito modular — dado o âmbito do projeto (final de curso + portfólio júnior), qualquer forma de distribuição seria overengineering claro.

---

## 2026-08-22 — Modelo de dados: `TRANSFER` como tipo de transação com conta de destino

**Decisão**: `transactions.type` inclui `TRANSFER`, com `account_id` (origem) + `destination_account_id` (destino, nullable) + `category_id` obrigatoriamente `NULL` nesse caso.

**Porquê**: o enunciado do projeto exige distinguir uma transferência entre contas próprias (ex: Millennium → Revolut) de uma despesa real. Modelar a transferência como uma variante do mesmo tipo `transaction` (em vez de uma tabela `transfers` separada) mantém uma única fonte de verdade para "tudo o que mexe em saldos de contas", simplificando queries de saldo e histórico — o custo é a necessidade de uma constraint (`CHECK`) e de lógica no service para garantir que transferências nunca entram nos totais de receitas/despesas do dashboard.

**Alternativa que considerei e rejeitei**: tabela `transfers` própria, separada de `transactions`. Rejeitei por duplicar a necessidade de manter saldos de contas consistentes em dois sítios diferentes, e por complicar o histórico unificado de movimentos de uma conta.

---

## 2026-08-22 — Categorias com `type` (INCOME/EXPENSE)

**Decisão**: adicionar um campo `type` à tabela `categories`, não pedido explicitamente no enunciado inicial.

**Porquê**: transações de receita (`INCOME`) também beneficiam de categorização (ex: "Salário", "Freelance"), mas orçamentos (`budgets`) só fazem sentido para categorias de despesa. Sem este campo, a UI não teria forma de filtrar corretamente as categorias certas em cada formulário (transação de receita vs. despesa vs. orçamento).

---

## 2026-08-22 — Dinheiro: `NUMERIC(12,2)` + `Decimal`, não `float`

**Decisão**: todos os valores monetários são `NUMERIC(12,2)` no Postgres, mapeados para `Decimal` em Python.

**Porquê**: `float` usa representação binária de vírgula flutuante, que não representa exatamente a maioria dos valores decimais (ex: `0.1 + 0.2 != 0.3` em IEEE 754) — inaceitável para dinheiro. `NUMERIC` é o tipo do Postgres para aritmética decimal exata, e `Decimal` é o equivalente em Python.

**Alternativa que considerei**: guardar tudo em cêntimos (`BIGINT`), abordagem usada por alguns sistemas de pagamento reais para evitar por completo qualquer questão de casas decimais. Rejeitei para este projeto por obrigar a converter mentalmente "tudo em cêntimos" em todas as camadas (schemas, cálculos de orçamento/projeções, frontend), aumentando a carga cognitiva sem benefício real à escala de uma app pessoal. `NUMERIC`/`Decimal` é o padrão mais comum e mais fácil de justificar/entender numa defesa.

---

## 2026-08-22 — Autenticação: access token em memória + refresh token em cookie httpOnly

**Decisão**: access token JWT de curta duração devolvido no corpo da resposta e guardado em memória no frontend (nunca `localStorage`); refresh token de longa duração em cookie `httpOnly`/`Secure`/`SameSite=Lax`, com hash persistido em `refresh_tokens` para permitir revogação/logout real.

**Porquê**: `localStorage` é acessível a qualquer script JavaScript a correr na página, o que o torna vulnerável a XSS (um script malicioso conseguiria roubar o token). Um cookie `httpOnly` nunca é acessível a JavaScript, só é enviado automaticamente pelo browser ao backend. Persistir o refresh token (com hash, nunca em claro) permite invalidar sessões (logout, deteção de roubo) — sem essa tabela, um JWT válido seria válido até expirar, sem forma de o revogar antes disso.

---

## 2026-08-22 — Eliminação de categorias: `RESTRICT`, não `CASCADE`

**Decisão**: categorias associadas a transações/orçamentos/despesas recorrentes não podem ser eliminadas diretamente — a API devolve `409 Conflict`. O frontend deverá oferecer reatribuição a outra categoria antes de eliminar.

**Porquê**: apagar em cascata destruiria histórico financeiro real sem aviso. Numa aplicação de dinheiro, perder dados silenciosamente é um erro grave — prefiro obrigar a uma decisão explícita.

---

## 2026-08-22 — Simplificações de teste face ao âmbito de um projeto final de curso

**Decisão**: testes de integração usam Postgres real via `docker-compose` (local) e serviço nativo do GitHub Actions (CI), em vez de introduzir a biblioteca Testcontainers. Playwright E2E cobre 4–6 fluxos críticos, não uma suite exaustiva.

**Porquê**: o projeto tem de ser terminável no tempo que tenho disponível para um trabalho final de curso, e cada biblioteca extra é mais um conceito a saber explicar na defesa. Testcontainers e uma suite E2E exaustiva são boas práticas em contexto profissional de maior escala, mas aqui o mesmo valor de aprendizagem (testar contra uma base de dados real, cobrir os fluxos críticos de ponta a ponta) alcanço com menos peças móveis.

**Nota para a apresentação**: isto é um bom exemplo de trade-off consciente de engenharia — escolher a solução mais simples que ainda cumpre o objetivo, e saber justificar porque não escolhi a mais "avançada".

---

## 2026-08-22 — Camada visual do frontend: shadcn/ui + Framer Motion + Recharts

**Decisão**: componentes base com shadcn/ui (Radix + Tailwind, código copiado para o repositório), animações com Framer Motion, gráficos com Recharts.

**Porquê**: o projeto serve também de peça de portfólio para entrada no mercado como programador júnior, pelo que a UI final deve parecer um produto real, não um CRUD académico. As três escolhas são, cada uma, a opção mais usada/reconhecida no respetivo nicho do ecossistema React — o que as torna simultaneamente fáceis de justificar numa entrevista técnica e bem documentadas para resolver problemas durante o desenvolvimento.

**Alternativas que considerei**: Nivo e visx para gráficos (mais visualmente distintos ou mais controlo via D3, respetivamente, mas mais tempo/complexidade); Tailwind puro sem biblioteca de componentes (mais controlo, mais tempo manual). Escolhi Recharts e shadcn/ui por equilibrarem melhor "resultado visual" vs. "tempo de aprendizagem/implementação" dentro do prazo do projeto.

---

## 2026-08-22 — Como giro o git/GitHub

**Decisão que tomei**: toda a gestão de git e GitHub (init, commits, branches, push, PRs, Actions) é sempre feita por mim manualmente. Este diário não regista commits/pushes, só decisões técnicas e de arquitetura.

**Porquê**: quero manter controlo total sobre o histórico do repositório e o GitHub, e nunca automatizar isso.

---

## 2026-08-22 — Fase 0: setup do repositório

**O que criei**: `backend/` (FastAPI mínimo com endpoint `/health` + teste), `frontend/` (Vite + React + TypeScript + Tailwind v4, página que consome `/health`), `docker-compose.yml` (postgres + backend + frontend), Dockerfiles de dev para ambos, workflow de CI (`lint-backend` com ruff, `lint-frontend` com oxlint). Sem `git init` nem qualquer ação de GitHub ainda nesta fase.

**Ambiente da máquina nesta altura**: só tinha Node/npm instalado, ainda sem Python nem Docker. O frontend instalei e verifiquei a construir (`npm run build`) e a passar lint (`npm run lint`) com sucesso. O backend escrevi mas **ainda não consegui correr/testar** — faltava-me instalar Python 3.12+ e [uv](https://docs.astral.sh/uv/) para `uv sync` + `uv run pytest`/`uv run uvicorn`, e Docker Desktop para `docker compose up`.

**Decisão — uv como gestor de dependências Python**: em vez de `pip` + `requirements.txt` ou Poetry. `uv` é uma ferramenta única (substitui pip, venv e pip-tools), muito mais rápida, e tornou-se a recomendação mais comum no ecossistema FastAPI em 2025/2026 — bom argumento de "ferramentas modernas" no CV. `pyproject.toml` usa `[dependency-groups]` (PEP 735) para separar dependências de produção das de desenvolvimento (`pytest`, `ruff`, `httpx`).

**Decisão — Tailwind CSS v4 via plugin do Vite**: a v4 elimina o ficheiro `tailwind.config.js`/`postcss.config.js` tradicional — basta `@import "tailwindcss";` no CSS e o plugin `@tailwindcss/vite`. Menos ficheiros de configuração para explicar.

**Decisão — CORS com origens explícitas, não wildcard**: `CORSMiddleware` está configurado com `allow_origins=["http://localhost:5173"]` (não `"*"`) porque `allow_credentials=True` (necessário mais tarde para cookies de refresh token) **não é permitido** pela especificação CORS em conjunto com `allow_origins="*"`. Ficar já com origens explícitas evita ter de voltar atrás nesta configuração na Fase 2.

**Problema que encontrei e resolvi**: o template Vite gerado nesta máquina já vinha com `oxlint` em vez de ESLint (linter em Rust, mais rápido) — mantive tal como veio, cumpre o mesmo papel de "Lint" no pipeline de CI. Também apareceram dois avisos menores ao configurar o alias de import `@/*` (usado mais tarde pelo shadcn/ui): a opção `baseUrl` está deprecated no TypeScript recente (resolvi usando `paths` sem `baseUrl`) e o Vite avisou sobre uso de `__dirname` no `vite.config.ts` (resolvi trocando para `import.meta.dirname`, a forma recomendada em módulos ESM).

**Como correr** (depois de instalar Python+uv e/ou Docker): ver `README.md` na raiz do projeto.

**Revisão — o que este passo me ensinou**: estrutura de projeto full-stack desde o início (backend e frontend como módulos independentes que comunicam por HTTP), configuração de CORS e porque importa, gestão de dependências moderna em Python (uv) vs. Node (npm), e a diferença entre "Dockerfile de desenvolvimento" (hot-reload, volumes montados) e "Dockerfile de produção" (build otimizado) — esta última fica para mais tarde.

---

## 2026-08-22 — Instalação do ambiente (Python, uv) e primeira validação real do backend

**Instalei**: Python 3.12.10 e uv 0.12.5, ambos via `winget` (gestor de pacotes nativo do Windows) — evita ter de descarregar instaladores manualmente e é fácil de repetir/documentar.

**Problema que encontrei e resolvi — `uv sync` falhava a construir o projeto**: ao correr `uv sync` pela primeira vez, o build falhou com `Unable to determine which files to ship inside the wheel` (erro do Hatchling, o build backend declarado em `[build-system]`). Causa: o nome do projeto no `pyproject.toml` (`fintrack-backend`) não corresponde a nenhuma pasta no disco (a pasta chama-se `app/`), e o Hatchling tenta adivinhar automaticamente qual o pacote a incluir no wheel a partir do nome do projeto. Como isto é uma **aplicação** (corre com `uvicorn`), não uma **biblioteca** a ser publicada/instalada por outros via `pip install`, a correção correta não é configurar manualmente o "package discovery" do Hatchling — é dizer ao uv para nem tentar construir um pacote instalável: acrescentei `[tool.uv]\npackage = false` ao `pyproject.toml`, e removi a secção `[build-system]` (deixou de ser necessária). Depois disto, `uv sync` instalou as 30 dependências sem problemas.

**Validei**: `uv run pytest` (1 teste a passar), `uv run ruff check .` (sem avisos), e o servidor real (`uv run uvicorn app.main:app`) a responder `200 OK` em `/health` com o corpo esperado.

**Nota técnica (não é um bug, só uma curiosidade de ambiente)**: nesta sessão, o `PATH` do Windows só foi atualizado no registo do sistema pelo `winget`, mas o terminal que já tinha aberto continuava com o `PATH` antigo — por isso tive de recarregar o `PATH` manualmente a partir do registo em cada comando (`$env:Path = ... GetEnvironmentVariable(...)`). Ao abrir um terminal novo (PowerShell, Git Bash, etc.) depois desta instalação, `python` e `uv` já funcionam diretamente, sem qualquer passo extra.

---

## 2026-08-22 — Docker Desktop: não consegui instalar automaticamente

**Situação**: ao verificar os pré-requisitos, confirmei que o **WSL2 não estava instalado** nesta máquina (`wsl --status` devolveu "não está instalado"). O comando para o instalar (`wsl --install`) precisa de privilégios de administrador e de reiniciar o computador — segui os passos manualmente.

**Resolvido**: instalei o WSL2 (`wsl --install`, reiniciei o PC) e o Docker Desktop. Após o reinício, a app Docker Desktop ainda não estava a correr (`docker compose up` falhava com `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` — o pipe do engine não existia porque a aplicação não tinha sido aberta). Arranquei a aplicação (`Docker Desktop.exe`) e, passado o tempo normal de arranque do engine (~30–60s), `docker version` já respondia com o servidor. `docker compose up -d` subiu os 3 containers com sucesso — ver "Estado atual" no topo do ficheiro.

---

## 2026-08-22 — Nova funcionalidade: Households (agregado familiar)

**Ideia**: quero poder criar um "agregado familiar" juntando a minha conta à da minha mulher (ex: Antonio + Teresa), com um toggle no painel central entre vista "Individual" (só os meus dados) e vista "Agregado Familiar" (dados combinados dos dois — rendimentos somados, etc.).

**Decisão de modelo**: contas e transações continuam sempre a pertencer ao `user_id` individual — não há "conta conjunta" real na BD. O agregado familiar é uma camada de **agregação em tempo de leitura**: três tabelas novas, `households`, `household_members` (com `UNIQUE(user_id)` — um utilizador só pertence a um agregado de cada vez) e `household_invites` (convite a um utilizador já registado, estado `PENDING/ACCEPTED/DECLINED`, nunca automático). O dashboard em modo "Agregado Familiar" identifica todos os `user_id` do agregado do utilizador atual e soma os dados de todos, em vez de filtrar só pelo utilizador autenticado.

**Porquê esta abordagem**: mantém zero alterações ao modelo já desenhado para `accounts`/`transactions`/`budgets`/etc. — cada pessoa mantém sempre o seu histórico individual privado e intacto, e a vista "Individual" nunca deixa de existir. Modelar como "conta conjunta" física (ex: uma `account` partilhada por dois `user_id`) obrigaria a repensar autorização em todas as tabelas de domínio (que hoje assumem um único `user_id` dono); a agregação em tempo de leitura evita essa reestruturação e é mais simples de justificar/testar.

**Porquê exigir aceitar convite**: juntar-se a um agregado implica expor dados financeiros pessoais a outra pessoa — não deve poder ser feito unilateralmente por quem convida.

**Roadmap**: adicionei a Fase 7 "Households" (a seguir ao Dashboard v1 — faz sentido só depois de existirem contas/transações reais para agregar), fases seguintes renumeradas. Ver `docs/ARCHITECTURE.md` secções 2, 4, 5, 8 para o desenho completo (tabelas, ERD, decisão). Implementação em si fica para quando chegar a essa fase — por agora só o desenho ficou registado.

---

## 2026-08-22 — Fase 1: base de dados (engine/session, Alembic, modelo `User`)

**Situação em que encontrei o projeto**: parte do trabalho desta fase já tinha feito numa sessão anterior que não cheguei a registar no diário (o PC bloqueou a meio) — `app/db/base.py`, `app/db/session.py`, `app/models/user.py` e o esqueleto do `alembic/` (com `env.py` já a importar `Base.metadata` e `settings.database_url`) já existiam e estavam corretos face ao modelo definido no `ARCHITECTURE.md`. Faltava: gerar e aplicar a primeira migração, e configurar `pytest` para correr testes de integração contra o Postgres real (agora que o Docker já está validado).

**Fiz**:
- `uv run alembic revision --autogenerate -m "create users table"` + `uv run alembic upgrade head` — tabela `users` criada no Postgres do `docker-compose` (confirmei via `psql \d users`).
- Reorganizei os testes para a estrutura documentada no `ARCHITECTURE.md` (`tests/unit/`, `tests/integration/`, `tests/api/`) — `test_health.py` mudou-se para `tests/api/`.
- Adicionei `tests/integration/conftest.py` com fixture `db_session`: abre uma ligação real ao Postgres, começa uma transação, e reverte-a sempre no fim do teste (mesmo em caso de erro), para os testes nunca deixarem lixo na base de dados. Precisei de um `if transaction.is_active` antes do `rollback()` porque, quando um teste força um `IntegrityError` (ex: violação de UNIQUE), o Postgres já aborta a transação sozinho — tentar reverter uma segunda vez dava um `SAWarning`.
- Adicionei `tests/integration/test_user_model.py`: cria e lê um `User` (valida UUID gerado, default `currency='EUR'`, `Decimal` a manter precisão), e um segundo teste que confirma que a constraint `UNIQUE(email)` é mesmo aplicada pela BD.

**Decisão — `alembic/versions/` excluído do ruff**: o ficheiro de migração gerado automaticamente usa `typing.Union`/`typing.Sequence` (não o estilo `X | Y` do resto do projeto) e ultrapassa o limite de 100 colunas em algumas linhas — é o template oficial do Alembic, não faz sentido reescrever à mão cada migração gerada só por estilo. Acrescentei `extend-exclude = ["alembic/versions"]` ao `[tool.ruff]` no `pyproject.toml`.

**Nota**: o `.github/workflows/ci.yml` ainda só faz lint (comentário no próprio ficheiro já dizia "cresce na Fase 13 para incluir testes e build") — por isso os testes de integração desta fase só correm localmente para já, contra o Postgres do `docker-compose`; o serviço Postgres no CI fica para a Fase 13, como já estava planeado.

**Validei**: `uv run pytest` (3 testes a passar: health check + 2 testes de integração do `User`), `uv run ruff check .` (limpo).

---

## 2026-08-22 — Fase 2 (backend): autenticação — registo, login, refresh, logout

**Objetivo**: implementar o fluxo de autenticação completo definido no `ARCHITECTURE.md` — access token JWT curto em memória no frontend, refresh token de longa duração em cookie `httpOnly`, com revogação/rotação real via tabela `refresh_tokens`.

**Camadas que criei** (primeira vez que o projeto usa a estrutura completa `api → schemas → services → repositories → models`, definida na Fase 0 mas só agora preenchida):
- `app/core/security.py` — hashing de password, criar/validar JWT, gerar e fazer hash do refresh token.
- `app/core/exceptions.py` — exceções de domínio (`EmailAlreadyRegisteredError`, `InvalidCredentialsError`, `InvalidRefreshTokenError`), traduzidas para respostas HTTP só na camada `api/` (o `service` não sabe o que é um `HTTPException`).
- `app/models/refresh_token.py` + migração Alembic.
- `app/schemas/user.py`, `app/schemas/auth.py` — validação Pydantic dos pedidos/respostas.
- `app/repositories/user_repository.py`, `refresh_token_repository.py` — só queries, sem regra de negócio.
- `app/services/auth_service.py` — orquestra tudo: registar, autenticar, rodar refresh token, logout.
- `app/api/deps.py` — `get_current_user` (dependency do FastAPI que lê o header `Authorization: Bearer ...`).
- `app/api/v1/auth.py` (`/register`, `/login`, `/refresh`, `/logout`) e `app/api/v1/users.py` (`/users/me`, primeira rota protegida — prova que o mecanismo de autorização funciona de ponta a ponta).

**Decisão — registo faz login automático**: `/register` já devolve `access_token` + define o cookie de refresh, tal como `/login` — evita ter de submeter as credenciais duas vezes seguidas (registar, depois logar) só para começar a usar a app.

**Decisão — mensagem de erro genérica no login**: `401 "Email ou password inválidos."` tanto para email inexistente como para password errada, de propósito — nunca revelar qual dos dois estava errado, para não permitir a um atacante descobrir que emails têm conta.

**Decisão — cookie de refresh restrito a `Path=/api/v1/auth`**: o cookie só é enviado pelo browser nos pedidos a `/api/v1/auth/*` (registo/login/refresh/logout), nunca nos outros pedidos à API. O access token é que vai no header `Authorization` em todos os outros pedidos. Reduz a superfície de exposição do cookie.

**Problema 1 — `passlib` incompatível com o `bcrypt` atual**: ao correr os primeiros testes, `hash_password` rebentava com `ValueError: password cannot be longer than 72 bytes`. Investiguei: o `passlib` (a biblioteca que o `ARCHITECTURE.md` tinha planeado usar) não tem release desde 2020 e faz uma verificação interna de "bug de wraparound" do bcrypt usando uma password de teste propositadamente longa; versões modernas do `bcrypt` (a partir da 4.1) deixaram de truncar passwords >72 bytes silenciosamente e passaram a levantar erro — o que faz essa verificação interna do `passlib` rebentar antes mesmo de qualquer código meu correr. Tinha dois caminhos: fixar `bcrypt<4.1` (mantém `passlib`, mas prende o projeto a uma versão antiga de uma dependência de segurança) ou deixar de usar o `passlib` e chamar `bcrypt` diretamente (só precisava de duas funções, `hashpw`/`checkpw`). Optei pela segunda — mais simples, sem a camada de abstração de uma biblioteca não mantida, e resolve o problema na raiz em vez de o mascarar. Efeito secundário: como o `bcrypt` novo já não trunca silenciosamente, tive de acrescentar `max_length=72` ao campo `password` no schema Pydantic de registo, para o próprio pedido ser rejeitado com um erro de validação claro (`422`) em vez de a app rebentar a meio do hashing.

**Problema 2 — commits dos testes de API "vazavam" para a base de dados real**: o padrão que usei na Fase 1 para os testes de integração (abrir uma transação e reverter sempre no fim) partia do princípio de que o código sob teste nunca chamaria `commit()`. Os endpoints de auth chamam `db.commit()` a sério (para os utilizadores/refresh tokens ficarem persistidos entre pedidos HTTP). Um `session.commit()` numa sessão ligada diretamente a uma `connection` com uma transação manual **termina essa transação externa** — ou seja, os dados de teste ficariam mesmo gravados na base de dados de desenvolvimento, e testes a correr outra vez podiam colidir com o `UNIQUE(email)`. Corrigi usando o modo `join_transaction_mode="create_savepoint"` do SQLAlchemy 2.0: cada `commit()` do código da aplicação passa a libertar/reabrir um `SAVEPOINT` em vez de terminar a transação externa, que só é mesmo revertida no fim de cada teste. Documentei com um comentário no `tests/conftest.py` — é um detalhe subtil que vale a pena saber explicar na defesa.

**Problema 3 — container Docker do backend com dependências desatualizadas**: depois de tudo passar nos testes (correndo diretamente na máquina, fora do Docker), o container `backend` continuava a rebentar com `ModuleNotFoundError: No module named 'sqlalchemy'` ao arrancar. Causa: o `docker-compose.yml` só monta `./backend/app` como volume (para hot-reload do código) — o ambiente Python (`.venv`) fica sempre preso ao que existia no momento do `docker build`, e a imagem tinha sido construída na Fase 0, antes de SQLAlchemy/Alembic/psycopg (Fase 1) e agora bcrypt/PyJWT (Fase 2) serem adicionados ao `pyproject.toml`. `docker compose up` sozinho **não** reconstrói a imagem automaticamente quando só o `pyproject.toml` muda. Resolvi com `docker compose build backend` seguido de `docker compose up -d backend`. **Lição a lembrar nas próximas fases**: sempre que acrescentar uma dependência nova ao backend, tenho de reconstruir a imagem Docker antes de testar lá — o hot-reload do volume só cobre mudanças ao código, não ao `pyproject.toml`/`.venv`.

**Validei end-to-end**: além de `uv run pytest` (14 testes: 4 de segurança unitários, 7 de API de auth incluindo rotação de refresh token e revogação, 2 de integração do modelo `User`, 1 de health check) e `uv run ruff check .` (limpo, com `extend-immutable-calls` adicionado ao `pyproject.toml` para o ruff parar de assinalar `Depends(...)` do FastAPI como bug), testei o fluxo completo a sério contra o container Docker real com `curl`: registo → `/users/me` com e sem token → `/refresh` (token rodado) → `/logout` (refresh token revogado). Apaguei o utilizador de teste da BD de desenvolvimento no fim.

**Por fazer nesta fase**: páginas de login/registo no frontend, contexto React para o access token em memória, interceptor para renovar automaticamente via `/refresh` quando o access token expira, e rotas protegidas no React Router.

---

## 2026-08-22 — Fase 2 (frontend): login, registo, rotas protegidas

**Dependências novas**: `react-router-dom`, `@tanstack/react-query`, `react-hook-form`, `zod` + `@hookform/resolvers`, `clsx`/`tailwind-merge`/`class-variance-authority` (utilitários do shadcn/ui), `lucide-react`, `motion` — todas já previstas no `ARCHITECTURE.md`.

**Estrutura que criei** (primeira vez que o frontend sai do "hello world" da Fase 0):
- `src/api/token-store.ts` — o access token vive **fora da árvore React**, num módulo simples com um pequeno pub/sub (`subscribeAccessToken`). Porquê: o cliente HTTP (`src/api/client.ts`) precisa de ler/escrever o token em código que corre fora de componentes React (dentro de uma função `fetch`), e o `AuthContext` também precisa de o refletir. Um módulo à parte evita ter de passar o token manualmente por todo o lado.
- `src/api/client.ts` — wrapper à volta de `fetch` com renovação automática: se um pedido responde `401`, tenta uma vez `refreshSession()` (chama `/api/v1/auth/refresh` usando o cookie httpOnly) e repete o pedido original com o novo access token. Só falha a sério se o refresh também falhar (sessão mesmo expirada).
- `src/features/auth/` — `types.ts`, `api.ts` (chamadas HTTP), `context.ts` (o `React.Context`, à parte do provider por razões explicadas abaixo), `auth-context.tsx` (`AuthProvider`), `use-auth.ts` (hook `useAuth()`).
- `src/components/ui/` — `button.tsx`, `input.tsx`, `label.tsx`, `card.tsx`: primitivas no estilo shadcn/ui, escritas à mão (Tailwind + `class-variance-authority` para variantes) em vez de correr o CLI `shadcn add` — mais previsível assim, mesmo resultado final (código copiado para o repositório, sem dependência de runtime).
- `src/routes/login.tsx`, `register.tsx` — formulários com `react-hook-form` + validação `zod`, ligados ao `useAuth()`.
- `src/routes/protected-route.tsx` — redireciona para `/login` se não autenticado; mostra um estado de "a carregar" enquanto a Fase 2 ainda está a tentar renovar a sessão a partir do cookie.
- `App.tsx` passou a ser só a configuração de rotas (`react-router-dom`); `main.tsx` ganhou o `QueryClientProvider` do TanStack Query (usado a partir da Fase 3 em diante para os pedidos de dados).

**Decisão — arranque da app tenta sempre `/refresh` primeiro**: como o access token só vive em memória, um F5 na página perdia sempre a sessão se não houvesse este passo. O `AuthProvider`, ao montar, chama `refreshSession()` uma vez; se o cookie de refresh ainda for válido, continuo autenticado sem ter de fazer login outra vez — só perco a sessão de facto quando o refresh token expira (30 dias) ou faço logout.

**Decisão — `AuthContext` (o objeto `createContext`) num ficheiro à parte do `AuthProvider`**: o `oxlint` (linter usado no projeto) avisou (`react(only-export-components)`) que um ficheiro que exporta um componente React e também um valor não-componente (o `Context`) parte o Fast Refresh do Vite (perde-se o estado do componente a cada hot-reload durante o `npm run dev`). Resolvi movendo o `Context`/tipos para `src/features/auth/context.ts`, ficando `auth-context.tsx` só com o componente `AuthProvider`.

**Simplificação consciente, a rever se vier a ser problema**: se um pedido a meio da sessão falhar a renovar (refresh token realmente expirado), o `AuthContext` só fica "desatualizado" (continua a mostrar o utilizador como autenticado) até à próxima ação que dependa da API — não há ainda um mecanismo global que force logout automático nesse caso preciso. Como só existe uma rota protegida (o dashboard placeholder) nesta fase, o impacto é mínimo; anotei para revisitar quando houver mais pedidos de dados espalhados pela app (Fase 3 em diante), por exemplo com um handler de erro global do TanStack Query.

**Confirmei, não assumi — como o dinheiro chega ao frontend**: testei diretamente com Python/Pydantic que um campo `Decimal` é sempre serializado como **string** em JSON (`"12.50"`, nunca `12.5` como número) — por isso tipei `monthly_income` como `string | null` no frontend (`features/auth/types.ts`), não `number`. Confirma na prática a decisão da secção 8 do `ARCHITECTURE.md` de nunca deixar dinheiro passar por um `number`/`float` do JavaScript.

**Validei**: `npm run build` (tsc + vite build, sem erros) e `npm run lint` (oxlint, limpo). Reconstruí a imagem Docker do frontend (mesmo motivo do backend — `docker-compose.yml` só monta `src/`/`public/` como volume, `node_modules` fica preso ao `npm ci` do `docker build`; `npm install` de pacotes novos no host nunca chega ao container sozinho). Confirmei por `curl` que o servidor Vite dentro do Docker serve a shell da SPA corretamente.

**Por verificar manualmente no browser** (ainda não tinha testado visualmente nesta sessão): abrir `http://localhost:5173`, confirmar que redireciona para `/login` (sem sessão), registar uma conta, confirmar que cai no dashboard já autenticado, testar "Terminar sessão", e voltar a entrar com as mesmas credenciais.

---

## 2026-08-22 — Confirmação visual do fluxo de autenticação

**Testei end-to-end no browser real** (containers Docker, `http://localhost:5173`):
1. Acesso sem sessão a `/` → redireciona para `/login`. OK.
2. Registo de conta nova (`/registar`) → login automático, cai no dashboard placeholder já autenticado. OK.
3. Nova navegação para `/` (equivalente a F5) → sessão mantida via `refreshSession()` a partir do cookie httpOnly, sem precisar de novo login. OK.
4. "Terminar sessão" → revoga o refresh token e redireciona para `/login`. OK.
5. Login de novo com as mesmas credenciais → sucesso. OK.
6. Login com password errada → mensagem genérica "Email ou password inválidos." (nunca revela qual dos dois campos está errado, como decidi na Fase 2). OK.

**Observação (não bloqueante)**: numa das repetições do passo 3, logo a seguir ao registo, a navegação para `/` mostrou por breves instantes o formulário de `/login` em vez do dashboard, antes de recarregar e confirmar que a sessão afinal persistia (repetições seguintes do mesmo passo funcionaram sempre à primeira). Suspeita: possível condição de corrida entre o `Set-Cookie` do `/register` ainda não estar totalmente aplicado pelo browser e a chamada a `refreshSession()` no arranque do `AuthProvider` — não investiguei a fundo porque não se repetiu de forma consistente. Fica anotado para vigiar: se voltar a acontecer de forma reprodutível numa fase futura (com mais tráfego de rede a atrasar o pedido de registo), vale a pena revisitar a ordem `register → set cookie → redirect` no backend ou adicionar um pequeno retry/espera no frontend.

**Limpeza**: apaguei o utilizador de teste (`antonio.teste.fintrack@example.com`) da tabela `users` no Postgres de desenvolvimento no fim (`docker compose exec postgres psql -U fintrack -d fintrack -c "DELETE FROM users WHERE email = '...'"`).

**Validei**: fluxo de autenticação da Fase 2 dado como completo e confirmado visualmente. Sem alterações de código nesta sessão.

---

## 2026-08-22 — Fase 3: Accounts (CRUD completo, backend + frontend)

**Objetivo**: primeira funcionalidade de domínio real da app — CRUD de contas financeiras (`accounts`), com `current_balance` mantido pelo service layer conforme desenhei no `ARCHITECTURE.md`.

**Backend** (segue exatamente a estrutura em camadas da Fase 2 — `api → schemas → services → repositories → models`):
- `app/models/account.py` — modelo `Account` + enum `AccountType` (`BANK`/`WALLET`/`SAVINGS`/`CREDIT_CARD`/`OTHER`). Usei `enum.StrEnum` (não `class X(str, enum.Enum)`) porque o `ruff` (regra `UP042`) sinaliza a segunda forma como obsoleta desde o Python 3.11.
- `app/schemas/account.py` — `AccountCreate`, `AccountUpdate` (todos os campos opcionais, para `PATCH` parcial), `AccountRead`.
- `app/repositories/account_repository.py` — `list_by_user`, `get_by_id_for_user` (filtra sempre por `user_id`, nunca só por `id` — é o que impede um utilizador aceder/editar contas de outro), `create`, `delete`.
- `app/services/account_service.py` — a decisão mais importante desta fase: **`update_account` nunca sobrescreve `current_balance` diretamente a partir de um novo `initial_balance`; aplica só a diferença** (`delta = novo - antigo; current_balance += delta`). Porquê: a partir da Fase 5 (Transactions), `current_balance` vai divergir de `initial_balance` à medida que transações forem lançadas. Se a edição do saldo inicial simplesmente copiasse o valor para `current_balance`, editar o nome de uma conta anos depois de criada apagaria silenciosamente o efeito de todas as transações já lançadas. Aplicar só o delta é correto tanto agora (sem transações, delta = valor novo) como mais tarde (com transações, preserva o que elas já ajustaram).
- `app/api/v1/accounts.py` — `GET/POST /accounts`, `PATCH/DELETE /accounts/{id}`, todos atrás de `get_current_user` (o mesmo dependency da Fase 2).
- Migração Alembic `create accounts table` gerada e aplicada.
- Testes (`tests/api/test_accounts.py`, 7 testes): criar conta, listar só as próprias (utilizador B não vê contas do utilizador A), o delta de `current_balance` ao editar `initial_balance`, editar nome não mexe no saldo, um utilizador não consegue editar conta de outro (`404`, não `403` — de propósito, para não revelar que o `id` existe), eliminar, e exigência de autenticação. 21 testes a passar no total (14 anteriores + 7 novos), `ruff check` limpo.

**Frontend**:
- `src/features/accounts/` (`types.ts`, `api.ts`, `schemas.ts`) e `src/routes/accounts.tsx` — primeira página a usar o TanStack Query já configurado desde a Fase 2 (`useQuery` para listar, `useMutation` + `invalidateQueries` para criar/editar/eliminar).
- Novo componente `components/ui/select.tsx` (não existia até agora) e variante `destructive` em `components/ui/button.tsx`.
- **Decisão — eliminar conta pede confirmação inline, nunca `window.confirm()`**: um `confirm()` nativo do browser bloqueia a thread de JavaScript e é geralmente pior UX/mais difícil de testar. Implementei como estado local (`confirmingDelete`) que troca os botões "Editar/Eliminar" por "Confirmar/Cancelar" na própria linha da conta.
- Rota `/contas`, protegida como o dashboard, com link a partir do dashboard ("Ver contas").

**Problema — Vite dentro do Docker não via alterações a ficheiros novos no Windows**: depois de criar `src/routes/accounts.tsx` e atualizar `src/App.tsx` com a nova rota, o browser continuava a mostrar "No routes matched location /contas" mesmo depois de recarregar a página. Diagnóstico: `docker compose exec frontend cat /app/src/App.tsx` confirmou que o ficheiro montado (bind mount `./frontend/src:/app/src`) **já tinha o conteúdo novo** — não era um problema de sincronização de ficheiros, era o `chokidar` (watcher interno do Vite) a nunca disparar o evento de mudança. Causa: bind mounts do Docker Desktop no Windows não propagam eventos `inotify` para dentro do container Linux — o ficheiro muda no disco, mas o processo dentro do container nunca é avisado, por isso o Vite continuava a servir a transformação em cache do módulo antigo. **Corrigi** adicionando `server.watch.usePolling: true` ao `vite.config.ts` (força o Vite a verificar ficheiros periodicamente em vez de esperar por eventos do SO). Como `vite.config.ts` está na raiz do `frontend/` e **não** é um caminho montado como volume (só `src/` e `public/` o são), foi preciso `docker compose build frontend` + `docker compose up -d frontend` para a mudança chegar à imagem — um `up -d` sozinho não teria bastado. **Lição a lembrar**: esta configuração já fica feita de vez (não é algo a repetir a cada fase), mas explica por que o hot-reload pareceu "não funcionar" nesta sessão — vale a pena saber explicar na defesa se surgir a pergunta sobre Docker + Windows + dev experience.

**Validei end-to-end no browser real** (depois da correção acima): criar conta (Banco, saldo inicial 500,50 €) → aparece na lista com o saldo correto; editar saldo inicial para 600,50 € → saldo atual acompanha corretamente; eliminar com confirmação inline → volta ao estado vazio ("Ainda não tens nenhuma conta"). Apaguei o utilizador de teste da BD no fim.

---

## 2026-08-22 — Fase 4: Categories (CRUD completo, backend + frontend)

**Objetivo**: CRUD de categorias próprias do utilizador (`name` + `type` INCOME/EXPENSE), com `UNIQUE(user_id, name)` para evitar duplicados.

**Backend** (mesma estrutura em camadas das Fases 2/3):
- `app/models/category.py` — modelo `Category` + `CategoryType` (`enum.StrEnum`, mesma convenção da Fase 3). Campos `icon`/`color` incluídos no modelo/schema (cosméticos, conforme `ARCHITECTURE.md`) mas sem UI para os editar ainda — não há necessidade real até ao gráfico de despesas por categoria (Fase 6), por isso não construí um seletor de cor/ícone só por completude.
- `app/repositories/category_repository.py`, `app/services/category_service.py`, `app/api/v1/categories.py` — mesmo padrão de `list/get/create/update/delete` scoped a `user_id` da Fase 3.
- **Decisão — duplicado verificado na aplicação, não à espera do `IntegrityError` da constraint**: tal como o registo de utilizadores na Fase 2 (`get_by_email` antes de inserir), `create_category`/`update_category` verificam `get_by_name_for_user` antes de gravar, e traduzem para `409 Conflict` com mensagem clara. A `UNIQUE(user_id, name)` na BD continua a existir como rede de segurança (ex: contra condições de corrida), mas o caminho normal nunca deixa a exceção da BD chegar à API.
- **Decisão consciente — bloqueio de eliminação por "categoria em uso" ainda não implementado**: o requisito existe no `ARCHITECTURE.md` ("bloqueio de eliminação se houver transações associadas"), mas nesta fase **nenhuma tabela referencia `categories`** — `transactions`/`budgets`/`recurring_expenses` só chegam nas Fases 5/8/9, cada uma com a sua FK `ON DELETE RESTRICT`. Implementar agora um `try/except IntegrityError` para uma FK que ainda não existe seria código morto e não testável. Deixei documentado no próprio `delete_category` (comentário) para resolver quando a Fase 5 adicionar `transactions` — nessa altura, um `db.flush()` sobre uma categoria associada vai levantar `IntegrityError`, que passa a ser apanhado e traduzido em `409`.
- Migração Alembic `create categories table` gerada e aplicada.
- Testes (`tests/api/test_categories.py`, 9 testes): criar, duplicado do mesmo utilizador → `409`, nomes iguais entre utilizadores diferentes → permitido, listar só as próprias, editar nome, editar para um nome já usado → `409`, um utilizador não edita categoria de outro → `404`, eliminar, exigência de autenticação. 30 testes a passar no total, `ruff check` limpo.

**Frontend**: `src/features/categories/` + `src/routes/categories.tsx`, mesmo padrão da página de Contas (TanStack Query, formulário inline, confirmação de eliminação sem `window.confirm`). Rota `/categorias`, link a partir do dashboard.

**Bug de UI que encontrei e corrigi — erro em linha espremia os campos do formulário**: testei no browser, ao submeter um nome duplicado a mensagem de erro entrava na mesma `flex-row` que os campos e os botões (`<form className="flex ... sm:flex-row ...">` com o erro como mais um item dessa linha) — sem `min-width`, os inputs ficavam espremidos a poucos pixels de largura (o campo "Nome" chegou a mostrar só "Al" de "Alimentação", embora o valor armazenado estivesse correto, só visualmente cortado). Corrigi em `routes/categories.tsx` e `routes/accounts.tsx` (mesmo padrão de formulário, mesmo bug nos dois): a linha `sm:flex-row` passou a conter só os campos e os botões, com a mensagem de erro fora dessa linha, numa linha própria a toda a largura por baixo. Confirmei visualmente que o layout se mantém legível mesmo com o erro visível.

**Validei end-to-end no browser real**: criar categoria "Alimentação" (Despesa) → aparece na lista; tentar criar outra igual → erro "Já existe uma categoria com este nome." visível e bem formatado; editar para "Restaurantes" → atualiza; eliminar com confirmação inline → volta ao estado vazio. Apaguei o utilizador de teste da BD no fim.

---

## 2026-08-22 — Fase 5: Transactions (a peça central do modelo, backend + frontend)

**Objetivo**: CRUD de transações (`INCOME`/`EXPENSE`/`TRANSFER`), com o service a manter `current_balance` das contas sempre consistente com o histórico de movimentos.

**Backend**:
- `app/models/transaction.py` — `Transaction` + `TransactionType`. FKs para `accounts`/`categories` com `ON DELETE RESTRICT` (primeira vez que essas FKs passam a existir de facto — ver "Problema/decisão" abaixo). Duas `CheckConstraint`: `amount > 0` e a forma de uma transferência (`type='TRANSFER' ⇒ destination_account_id NOT NULL AND category_id NULL`), replicando as regras já desenhadas no `ARCHITECTURE.md`.
- **Decisão — toda a validação de negócio vive no service, não replicada em dois schemas Pydantic**: `TransactionCreate` e `TransactionUpdate` são schemas "burros" (só tipos e `Field(gt=0)` no `amount`); a combinação tipo↔categoria↔conta-destino é validada uma única vez, em `_validate_combination` (`transaction_service.py`), chamada tanto por `create_transaction` como por `update_transaction`. Evitei duplicar a mesma lógica de validação em dois `model_validator` do Pydantic que facilmente divergiriam com o tempo.
- **Decisão — `TransactionUpdate` exige sempre o objeto completo, não é um PATCH parcial por campo** (ao contrário de `AccountUpdate`/`CategoryUpdate`): `type`, `category_id` e `destination_account_id` têm invariantes cruzadas — mudar de `EXPENSE` para `TRANSFER` tem de *limpar* `category_id` e *preencher* `destination_account_id` ao mesmo tempo. Um PATCH campo-a-campo tornaria ambíguo o que um `None` significa nesses dois campos ("não mexer" vs. "limpar porque o novo tipo não usa isto"). Assumo que a UI reenvia sempre o formulário completo ao editar uma transação — é o que a UI real faz (`routes/transactions.tsx` pré-preenche o formulário todo, nunca só um campo).
- **A lógica mais delicada — `_apply_balance_effect(type, account, destination, amount, sign)`**: uma única função com `sign=+1`/`sign=-1` aplica ou reverte o efeito de qualquer tipo de transação nos saldos. `update_transaction` usa-a duas vezes: primeiro com `sign=-1` sobre as contas *antigas* da transação (antes de editar) para desfazer o efeito anterior, depois com `sign=+1` sobre as contas *novas* (podem ser as mesmas ou diferentes, se mudar a conta). `delete_transaction` só chama a reversão. Isto garante que editar o valor, o tipo, ou até mudar de conta origem/destino nunca deixa saldos inconsistentes, sem repetir a fórmula em três sítios.
- **Decisão/problema — FK `RESTRICT` para `accounts`/`categories` finalmente existe, e as duas exigiam tratamento de `IntegrityError` que ainda não tinha escrito**: até esta fase, `account_service.delete_account`/`category_service.delete_category` apagavam sem verificação nenhuma porque nenhuma tabela os referenciava ainda (documentei assim na entrada da Fase 4). Agora que `transactions.account_id`/`destination_account_id`/`category_id` existem com `ON DELETE RESTRICT`, ambos os services passaram a fazer `try: db.flush() / except IntegrityError: db.rollback(); raise AccountInUseError/CategoryInUseError`, traduzido para `409` nos routers — exatamente como já tinha anotado que aconteceria. O `db.rollback()` só desfaz até ao savepoint mais recente (ver `tests/conftest.py`), não estraga a transação de teste externa.
- Nova query com `OR` no repositório (`transaction_repository.list_by_user`): filtrar por `account_id` tem de corresponder tanto a `account_id` como a `destination_account_id` — uma conta "aparece" no extrato tanto quando é origem como quando é destino de uma transferência.
- **Refactor de testes**: `_auth_headers`/`_create_account`/`_create_category` estavam a ser copiados e colados em cada novo ficheiro de teste (`test_accounts.py`, `test_categories.py`, e agora `test_transactions.py` ia ser o terceiro/quarto). Extraí para `tests/api/helpers.py` (`register_and_get_headers`, `create_account`, `create_category`), com os ficheiros existentes atualizados para os importar em vez de duplicar.
- Testes (`tests/api/test_transactions.py`, 16 testes): INCOME aumenta saldo, EXPENSE diminui, TRANSFER move entre contas, transferência para a própria conta rejeitada, transferência com categoria rejeitada, receita sem categoria rejeitada, categoria com tipo errado rejeitada, editar valor ajusta saldo pelo delta, editar mudando de conta move o efeito da conta antiga para a nova, eliminar reverte o saldo, filtros (conta/categoria/tipo/intervalo de datas), isolamento entre utilizadores, e os dois novos `409` (conta/categoria em uso). **45 testes a passar no total**, `ruff check` limpo (incluindo troca de `HTTP_422_UNPROCESSABLE_ENTITY`, que o Starlette já marca como *deprecated*, por `HTTP_422_UNPROCESSABLE_CONTENT`).

**Frontend**: `src/features/transactions/` + `src/routes/transactions.tsx` — o formulário mais complexo até agora: campo "Categoria" ou "Conta de destino" aparece/desaparece consoante o `type` escolhido (`useWatch` do `react-hook-form`), e a lista de categorias disponíveis filtra-se pelo tipo selecionado (só mostra categorias `INCOME` quando `type=INCOME`, etc.). Validação cruzada replicada no lado do cliente com `zod` `.superRefine()` (mensagens de erro imediatas, sem esperar pela resposta do servidor) — a validação a sério continua só no backend. Cartão de filtros (conta/categoria/tipo/intervalo de datas) usa `useQuery` com a `queryKey` a incluir o objeto de filtros, para o TanStack Query re-consultar automaticamente sempre que um filtro muda.

**Bug de UI que encontrei e corrigi — 409 de conta em uso não tinha para onde ir**: ao testar no browser, tentar eliminar uma conta com transações associadas falhava sem qualquer feedback visível — `routes/accounts.tsx` nunca tinha ganho o tratamento de erro de eliminação que `routes/categories.tsx` já tinha (adicionado na Fase 4, quando só categorias podiam ficar "em uso"). Corrigi com o mesmo padrão: `onError` na `deleteMutation` a guardar a mensagem num `useState` e a mostrar por baixo do nome da conta.

**Nota sobre ferramentas de teste, não sobre a app**: durante os testes manuais desta sessão, a extração de texto da página que estava a usar para verificação devolveu conteúdo desatualizado várias vezes seguidas (mostrava sempre o mesmo HTML antigo, como se a "nova transação" nunca tivesse aberto, mesmo depois de cliques bem-sucedidos). Diagnostiquei lendo o DOM ao vivo diretamente (`document.querySelector('main').innerText`) — a app estava sempre correta, só a ferramenta de extração é que ficava presa numa versão antiga da página nalguns momentos. Não é um bug da app; fica registado para não repetir a confusão numa sessão futura — se a extração de texto parecer "não refletir" uma ação, confirmar lendo o DOM/rede diretamente antes de assumir um bug de UI.

**Validei end-to-end no browser real**: criei um utilizador de teste com 2 contas (Millennium, Revolut) e 2 categorias (Alimentação/EXPENSE, Salário/INCOME). Despesa de 30€ → saldo da Millennium desce corretamente; transferência de 100€ Millennium→Revolut → saldos das duas contas movem-se corretamente; editar a despesa de 30€ para 50€ → saldo ajusta só pela diferença; eliminar a transferência → saldos das duas contas revertidos; filtro por tipo "Transferência" na lista funciona; tentativa de eliminar a categoria/conta em uso mostra a mensagem `409` na UI. Apaguei o utilizador de teste da BD no fim.

---

## 2026-08-27 — Fase 6: Dashboard v1 (resumo do mês + gráfico de despesas por categoria)

**Objetivo**: primeira vista que transforma o CRUD numa "app" — o resumo financeiro do mês selecionado, com saldo global, receitas/despesas, poupança e um gráfico de despesas por categoria.

**Decisão-chave — o dashboard é agregação em tempo de leitura, sem tabela nem migração nova**: não há tabela `dashboard_snapshots` nem colunas derivadas guardadas. O endpoint corre `SUM(...)`/`GROUP BY` sobre as `transactions` a cada pedido. Porquê: guardar totais persistidos criaria uma segunda fonte de verdade que teria de ser mantida em sincronia a cada `create`/`update`/`delete` de transação (e a cada edição de saldo de conta) — exatamente o tipo de duplicação que o `ARCHITECTURE.md` já rejeitou para `budgets` (secção 4). À escala desta app (uso pessoal, poucas centenas de transações por ano) uma agregação por pedido é instantânea e sempre correta. É o mesmo raciocínio que vai valer para os `budgets` (Fase 8) e o modo "Agregado Familiar" (Fase 7).

**Backend** (segue as camadas habituais, mas o `repository` aqui só tem queries de agregação, e o `service` não muta nada — nenhum `db.commit()` no router):
- `app/schemas/dashboard.py` — `DashboardSummary` + `CategoryExpense`. `savings_rate` é `float | None` (não `Decimal`): é um rácio para exibição, não um valor monetário, e `None` quando não houve receitas no mês (dividir por zero não tem significado útil). Todo o resto continua `Decimal`.
- `app/repositories/dashboard_repository.py` — `total_balance` (soma de `accounts.current_balance`, **não** filtrada por mês — é a fotografia "agora"), `sum_amount_by_type` (receitas/despesas do mês) e `expenses_by_category` (`JOIN categories` + `GROUP BY` + `ORDER BY SUM DESC`). Só `EXPENSE` entra no gráfico; `INCOME` e `TRANSFER` ficam de fora.
- **Decisão — intervalo de mês semi-aberto `[dia 1, dia 1 do mês seguinte[`** em `_month_bounds`, em vez de calcular "o último dia do mês": evita ter de saber se o mês tem 28/29/30/31 dias. O "mês seguinte" trata a passagem de dezembro→janeiro incrementando o ano.
- **Problema — `COALESCE(SUM(...), 0)` devolve `0` (inteiro), não `0.00`**: quando não há transações, o Postgres devolve o literal inteiro do `COALESCE`, e a API respondia `"0"` em vez de `"0.00"` (inconsistente com o resto, e os testes apanharam-no). Corrigi com um helper `_money()` no service que faz `.quantize(Decimal("0.01"))` a todos os totais antes de construir o schema.
- `app/api/v1/dashboard.py` — `GET /api/v1/dashboard`, parâmetro opcional `month` (qualquer dia do mês, formato ISO; omitido = mês atual). Registei no `main.py`.
- Testes (`tests/api/test_dashboard.py`, 8 testes): dashboard vazio de utilizador novo, totais + taxa de poupança, transferências ignoradas nos totais mas refletidas no saldo global, só conta o mês selecionado, `expenses_by_category` agrupado e ordenado, default para o mês atual, isolamento entre utilizadores, exige autenticação. **53 testes a passar no total**, `ruff` limpo.

**Frontend**:
- Dependência nova: **Recharts** (`npm install recharts`) — a biblioteca de gráficos já prevista no `ARCHITECTURE.md`. Reconstruí a imagem Docker do frontend (mesmo motivo das fases anteriores: `node_modules` fica preso ao `docker build`, só `src/` é volume).
- `src/features/dashboard/` — `types.ts`, `api.ts`, e `month.ts` (utilitários de navegação entre meses: `startOfMonth`/`addMonths`/`toIsoDate`/`monthLabel`, **sempre em hora local** — `toISOString()` converte para UTC e podia saltar um dia perto da meia-noite).
- `src/routes/dashboard.tsx` reescrito (era só um placeholder): cabeçalho com navegação (Contas/Categorias/Transações) + terminar sessão, navegador de mês (‹ ›, botão "Mês atual", seta "seguinte" desativada no mês corrente), 4 cartões de estatística (saldo global, receitas, despesas, poupança líquida + % em subtítulo), e um gráfico donut (Recharts `PieChart`) com uma legenda-lista ao lado a mostrar valor e % por categoria.
- **Decisão — paleta de cores de recurso no frontend**: o campo `categories.color` existe no modelo mas ainda não há UI para o editar (adiado desde a Fase 4). Enquanto isso, o gráfico usa uma paleta fixa de 8 cores indexada pela ordem da categoria. Quando a Fase 4 ganhar o seletor de cor, `item.color ?? FALLBACK[i]` já usa a cor real automaticamente.
- **Nit que corrigi no browser**: o rótulo do mês vinha "Agosto De 2026" (a classe Tailwind `capitalize` põe maiúscula em *cada* palavra). Troquei por capitalizar só a primeira letra em JS → "Agosto de 2026".

**Validei end-to-end no browser real**: utilizador de teste com 2 contas (saldo inicial 1000 + 200), 3 categorias, e no mês atual: receita 2000, despesas 320,50 (Alimentação) + 90 (Transporte), transferência 150 entre contas. O dashboard mostrou saldo global 2789,50 € (inclui a transferência, que não mexe nos totais de receita/despesa), receitas 2000,00 €, despesas 410,50 €, poupança 1589,50 € (79,5%), e o donut com Alimentação 78% / Transporte 22%. Naveguei para o mês anterior → tudo a zero + estado vazio "Sem despesas registadas neste mês", saldo global mantém-se (não é do mês). Apaguei o utilizador de teste da BD no fim.

**Bundle**: o `vite build` passou a avisar que o chunk único ultrapassa 500 kB (efeito do Recharts). Não fiz nada nesta fase — code-splitting por rota fica para o polish (Fase 16), onde faz mais sentido tratar disto de uma vez para toda a app.

---

## 2026-08-27 — Fase 7: Households (agregado familiar)

**Objetivo**: permitir juntar as finanças de duas (ou mais) pessoas num "agregado familiar", com um toggle no dashboard entre a vista individual e a vista combinada.

**Decisão central (já estava no `ARCHITECTURE.md`, agora implementada) — agregação em tempo de leitura, zero alterações às tabelas de domínio**: `accounts`/`transactions`/`categories` continuam a pertencer sempre a um `user_id` individual. Não há "conta conjunta". O agregado é só uma camada de leitura: quando o dashboard é pedido com `?scope=household`, o service resolve todos os `user_id` do agregado (via `household_members`) e soma os dados de todos. A vista "Individual" nunca desaparece, e o histórico de cada pessoa mantém-se privado.

**Impacto no código da Fase 6**: `dashboard_repository` deixou de receber um `user_id` e passou a receber `user_ids: Sequence[uuid.UUID]` (`WHERE user_id IN (...)`). Para a vista individual a lista tem um elemento; para o agregado tem N. A query é exatamente a mesma — foi a mudança mínima para suportar as duas vistas. O `DashboardSummary` ganhou um campo `scope` que ecoa a vista devolvida: se pedir `household` sem pertencer a um agregado, o service cai graciosamente em `individual` e diz isso na resposta (a UI só mostra o toggle quando há agregado, mas a API não deve rebentar se for chamada à mão).

**Modelo de dados** (migração `b280080ec37d`):
- `households` (`name`, `created_by`).
- `household_members` — **`UNIQUE(user_id)`**, não `UNIQUE(household_id, user_id)`: garante que cada pessoa só pertence a um agregado de cada vez, o que elimina qualquer ambiguidade no toggle ("qual agregado mostrar?").
- `household_invites` — estado `PENDING/ACCEPTED/DECLINED/CANCELLED`. **Índice único parcial** `WHERE status = 'PENDING'`: no máximo um convite pendente para a mesma pessoa no mesmo agregado, mas é possível reconvidar quem recusou (o convite antigo fica `DECLINED`, não conta). O `alembic revision --autogenerate` apanhou o `postgresql_where` corretamente a partir do `Index(..., postgresql_where=text(...))` no modelo — não precisei de editar a migração à mão.
- FKs todas `ON DELETE CASCADE` (a partir de `households` e de `users`) — apagar um agregado leva membros e convites com ele; apagar um utilizador idem. Confirmei na prática: apagar o utilizador criador limpou as 3 tabelas sem órfãos.

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

**Validei end-to-end no browser real** com dois utilizadores (Ana e Bruno), cada um com uma conta e transações próprias:
1. Ana cria "Família Teste" → aparece como membro com badge "Criador".
2. Ana convida Bruno por email → "Convite enviado a Bruno" + entra na lista de pendentes.
3. Bruno (nova sessão) vê o convite em "Convites recebidos" → aceita → passa a ver os dois membros.
4. Dashboard da Ana: o toggle aparece; "Individual" = só os dados dela (saldo 1800 €); "Agregado familiar" = **1980 €** de saldo, receitas 1500 €, despesas 320 € (200 dela + 120 dele), donut com as duas categorias "Casa" distintas (63% / 38%).
5. Dashboard do Bruno: "Individual" = saldo 180 €, sem receitas (poupança negativa a vermelho); "Agregado familiar" = os mesmos totais combinados.

Apaguei os utilizadores de teste no fim; confirmei que o `CASCADE` limpou `households`/`household_members`/`household_invites` sem deixar órfãos.

**Nota de UX conhecida (não bloqueante)**: na vista de agregado, duas categorias com o mesmo nome (ex: "Casa" da Ana e "Casa" do Bruno) aparecem como duas fatias separadas no gráfico, porque são de facto categorias distintas (cada uma do seu dono). Juntá-las por nome fica para os Insights (Fase 12), se se justificar — por agora, mostrar a verdade (categorias separadas) é mais correto do que fundir coisas que o modelo trata como diferentes.

---

## 2026-08-27 — Fase 8: Budgets (orçamento mensal por categoria)

**Objetivo**: definir um limite de gasto mensal por categoria de despesa e ver o progresso (gasto / restante / %) contra as transações reais do mês.

**Decisão central (já no `ARCHITECTURE.md` secção 4, agora implementada) — `spent`/`remaining`/`percentage` NÃO são colunas**: a tabela `budgets` só guarda `category_id` + `period_month` + `amount`. O "gasto" é calculado em runtime pelo service, somando as transações `EXPENSE` dessa categoria nesse mês. Guardar o valor gasto seria uma segunda fonte de verdade que teria de ser atualizada a cada `create`/`update`/`delete` de transação — o mesmo raciocínio do dashboard (Fase 6). `remaining = amount - spent` (pode ser negativo), `percentage = spent/amount*100` (pode passar de 100). `percentage` é `float` (rácio de exibição), tudo o resto é `Decimal`.

**Refactor — `month_bounds` extraído para `app/core/dates.py`**: o cálculo do intervalo semi-aberto `[dia 1, dia 1 do mês seguinte[` estava em `dashboard_service._month_bounds` e agora é preciso também nos orçamentos. Movi para um helper partilhado `app/core/dates.month_bounds(day)`; atualizei o `dashboard_service` para o importar. Segunda utilização = altura certa para extrair (não antes — teria sido abstração prematura).

**Modelo** (migração `c78b7f293320`):
- `budgets` — `UNIQUE(user_id, category_id, period_month)` (um orçamento por categoria por mês), `CHECK(amount > 0)`.
- `period_month` é sempre o **primeiro dia do mês** — o service normaliza qualquer data recebida (`period_month.replace(day=1)`) antes de gravar/consultar. Simplifica as queries "orçamentos deste mês" (igualdade exata em vez de intervalo).
- FK `category_id` → `categories` **`ON DELETE RESTRICT`** (seguindo a decisão da secção 5 do `ARCHITECTURE.md`). Não precisei de código novo: o `category_service.delete_category` já apanha qualquer `IntegrityError` de FK e devolve `409` — só atualizei a mensagem (`"...transações ou orçamentos..."`) para não mentir sobre a causa.

**Regras de negócio**:
- **Só categorias `EXPENSE` podem ter orçamento** (`422` se for `INCOME`) — orçamentar receitas não faz sentido. É o service que valida, não um `CHECK` (precisaria de um `JOIN` na constraint).
- **Um orçamento por (categoria, mês)** — verificado em código antes de gravar (`409`), com o `UNIQUE` como rede de segurança. Mesmo padrão das categorias (Fase 4).
- **Editar só permite mudar o `amount`** — a categoria e o mês *identificam* o orçamento; mudar qualquer um deles é, na prática, criar outro. `BudgetUpdate` só tem `amount`.

**Camadas**: `models/budget.py`, `schemas/budget.py`, `repositories/budget_repository.py` (inclui `spent_by_category` — `SUM ... GROUP BY category_id` das despesas do mês, devolve `dict[category_id, Decimal]`), `services/budget_service.py`, `api/v1/budgets.py` (`GET ?month=`, `POST`, `PATCH /{id}`, `DELETE /{id}`).
- Testes (`tests/api/test_budgets.py`, 12 testes): criar (spent 0), categoria `INCOME` → `422`, categoria inexistente → `404`, duplicado → `409` (mas mês seguinte ok), `spent` reflete só as transações do mês, orçamento ultrapassado (`remaining` negativo, `percentage` > 100), listagem scoped ao mês, editar valor recalcula o progresso, eliminar, isolamento entre utilizadores, eliminar categoria com orçamento → `409`, exige autenticação. **85 testes no total**, `ruff` limpo.

**Frontend**:
- Refactor: mudei `features/dashboard/month.ts` para **`src/lib/month.ts`** (agora partilhado com os orçamentos). Só o `dashboard.tsx` o importava; atualizei os imports.
- `features/budgets/` (`types.ts`, `api.ts`) + `src/routes/budgets.tsx` (rota `/orcamentos`): navegação por mês, formulário "novo orçamento" (só mostra categorias de despesa que ainda não têm orçamento nesse mês — quando esgotam, mostra "Todas as categorias de despesa já têm orçamento para este mês"), e uma lista com **barra de progresso colorida** (verde < 80%, âmbar 80–100%, vermelho > 100%, com a barra a saturar nos 100% mas a % real no texto), texto "X disponível" / "X acima do orçamento", editar valor inline e eliminar com confirmação inline (padrão anti-`window.confirm` das outras páginas). Link "Orçamentos" na navegação do dashboard.
- Formulário sem RHF/zod (só dois campos, um `<select>` + um valor) — `useState` simples com um regex de validação do valor, como a página do agregado. `oxlint`/`build` limpos.

**Validei end-to-end no browser real**: utilizador com 2 contas/categorias de despesa (Alimentacao, Transporte) e despesas no mês (180 + 75,50 em Alimentacao; 260 em Transporte).
1. Criar orçamento Alimentacao 200 € → "255,50 € / 200,00 € · 128%", barra **vermelha** cheia, "55,50 € acima do orçamento".
2. Criar orçamento Transporte 300 € → "260,00 € / 300,00 € · 87%", barra **âmbar**, "40,00 € disponível". Form passa a "todas as categorias já têm orçamento".
3. Editar Alimentacao para 400 € → recalcula para "255,50 € / 400,00 € · 64%", barra **verde**, "144,50 € disponível".
4. Naveguei para o mês seguinte → vazio + "Mês atual" aparece + form volta a oferecer as categorias.
5. Eliminei Transporte (confirmação inline) → desaparece, categoria volta a ficar disponível no form.

Apaguei o utilizador de teste da BD no fim.

---

## 2026-08-27 — Fase 9: Recurring Expenses (despesas recorrentes + geração de transações)

**Objetivo**: registar despesas que se repetem (renda, seguros, subscrições) e ter um mecanismo que cria as transações correspondentes sem lançar à mão todos os meses.

**Modelo** (migração `57804c58a457`): `recurring_expenses` com `account_id`/`category_id` (FK **`ON DELETE RESTRICT`**, como as transações), `description` (obrigatória — uma recorrência sem rótulo é inútil), `amount` (`CHECK > 0`), `frequency` (`MONTHLY`/`YEARLY`), `day_of_month` (`CHECK BETWEEN 1 AND 31`), `next_occurrence` (indexado), `active`.

**Decisão — `next_occurrence` é a fonte de verdade do "quando"; `day_of_month` só restaura o dia canónico**:
- Dou a **primeira ocorrência** como uma data (`next_occurrence`). Funciona igual para MONTHLY e para YEARLY (a tabela do `ARCHITECTURE.md` não tem `month_of_year`, e não valia a pena adicionar uma coluna — a data inicial já fixa o mês para o caso anual).
- `day_of_month` é derivado (`next_occurrence.day`) e guardado só para uma coisa: quando um mês curto força um recuo (31/jan → 28/fev), o avanço seguinte volta ao dia canónico (28/fev → **31**/mar). A função `advance()` avança sempre a partir de `day_of_month`, não de `current.day`, e faz `min(day_of_month, último_dia_do_mês_alvo)`.
- Testei em `tests/unit/test_recurrence.py` (5 testes, sem BD): clamp de mês curto, restauro do dia canónico, viragem de ano, anual, e o 29/fev de ano bissexto a cair em 28/fev.

**Decisão — a geração é `POST /recurring-expenses/generate`, invocada à mão (por agora)**: o `ARCHITECTURE.md` (secção 8) diz "invocado por um cron / GitHub Action / APScheduler". Para o âmbito do projeto, um botão "Gerar agora" na UI + uma nota de que em produção seria um job agendado é o MVP honesto — evita mais uma peça de infraestrutura a explicar. O serviço:
- Percorre as recorrências **ativas** com `next_occurrence <= hoje`.
- Para cada uma, faz **catch-up**: enquanto `next_occurrence <= hoje`, cria uma transação datada de `next_occurrence` e avança. Assim, se a app não for aberta durante 3 meses, ao gerar aparecem as 3 rendas em falta, cada uma no seu mês. Cap de `_MAX_CATCH_UP = 120` iterações por recorrência como rede de segurança contra um `next_occurrence` corrompido.
- **Cada transação passa pelo `transaction_service.create_transaction` normal** — a geração não é um caminho especial, os saldos das contas ficam consistentes de graça, e as transações geradas entram automaticamente no dashboard e nos orçamentos (são despesas reais).
- Se a categoria da recorrência tiver mudado de tipo para `INCOME` entretanto (estado inconsistente que criei via edição de categorias), a recorrência é **saltada** em silêncio na geração — continua a aparecer como "em atraso" na UI, por isso noto.

**Camadas**: `models/recurring_expense.py`, `schemas/recurring_expense.py` (`RecurringExpenseRead` inclui `account_name`/`category_name`/`is_due` resolvidos no service — `is_due = active AND next_occurrence <= hoje`), `repositories/recurring_expense_repository.py` (inclui `list_due_for_user`), `services/recurring_expense_service.py` (a função `advance()` é pública, para o teste unitário), `api/v1/recurring_expenses.py` (`GET`, `POST`, `POST /generate`, `PATCH /{id}`, `DELETE /{id}`).
- FKs RESTRICT novas para `accounts`/`categories` → o `account_service`/`category_service` já apanhavam qualquer `IntegrityError` de FK; só atualizei as mensagens de 409 ("...transações **ou despesas recorrentes**...").
- Testes API (`tests/api/test_recurring_expenses.py`, 12 testes): criar, categoria `INCOME` → 422, conta inexistente → 404, gerar cria 1 transação + avança + é idempotente, catch-up de vários meses (`generated == nº de transações`, saldo = inicial − generated×valor), saltar inativas e futuras, editar (valor/ativa/próxima-ocorrência re-deriva `day_of_month`), eliminar, isolamento entre utilizadores, eliminar conta/categoria em uso → 409, exige autenticação. **102 testes no total** (5 unit + 97 API/integração), `ruff` limpo.

**Frontend**: `features/recurring/` (`types.ts`, `api.ts`, `schemas.ts` com zod) + `src/routes/recurring.tsx` (rota `/recorrentes`): cartão "Gerar transações em falta" com contador de recorrências vencidas e feedback ("N transação(ões) gerada(s)" / "Nada a gerar — está tudo em dia"), formulário RHF+zod (descrição, valor, conta, categoria de despesa, frequência, próxima ocorrência, checkbox "Ativa"), e uma lista com badges "Em atraso"/"Pausada", botão rápido Pausar/Retomar, editar inline (mesmo `RecurringForm`) e eliminar com confirmação inline. `generate` invalida `recurring`/`transactions`/`accounts`/`budgets`/`dashboard`. Link "Recorrentes" na navegação do dashboard.

**Validei end-to-end no browser real**: conta Millennium (3000 €), categoria de despesa Habitacao. Criei recorrência "Renda" 550 €/mês com primeira ocorrência 15/06/2026 (hoje = 27/08) → aparece "Em atraso", contador "1 recorrência com ocorrências por lançar". "Gerar agora" → **"3 transação(ões) gerada(s)"**, badge desaparece, próxima ocorrência passa a 2026-09-15. A página de transações mostra as 3 "Renda" (−550 € em 15/06, 15/07, 15/08). Dashboard: saldo global **1350,00 €** (3000 − 3×550), despesas de agosto **550,00 €** (só a de 15/08 conta nesse mês — as outras estão nos seus meses), donut com Habitacao 100%. Apaguei o utilizador de teste no fim.

---

## 2026-08-27 — Fase 10: Financial Goals (objetivos + projeção de conclusão)

**Objetivo**: registar metas de poupança (fundo de emergência, férias, carro) com valor-alvo, valor já poupado e um prazo opcional, e mostrar quanto é preciso poupar por mês para lá chegar.

**Modelo** (migração `4569675ea483`): `goals` com `name`, `target_amount` (`CHECK > 0`), `current_amount` (`CHECK >= 0`, default 0), `deadline` (nullable). Sem FKs para contas/categorias — um objetivo é uma entidade autónoma (secção 5 do `ARCHITECTURE.md`: `USERS ||--o{ GOALS`). **Sem tabela de histórico de contribuições** — `current_amount` é uma coluna simples que ajusto diretamente, conforme o `ARCHITECTURE.md` (secção 4).

**Decisão — como muda o `current_amount`**:
- `PATCH /goals/{id}` edita qualquer campo diretamente (nome, alvo, valor, prazo).
- `POST /goals/{id}/contributions {amount}` é o caminho de UX preferido: penso em deltas ("meti 250 este mês"), não em totais. `amount` pode ser negativo para corrigir; o service rejeita (`422`) se o total ficasse < 0.

**Decisão — a projeção é orientada ao prazo, sem depender do histórico de transações**: `GoalRead` traz calculados em runtime: `remaining` (`max(alvo − atual, 0)`), `progress_percentage`, `is_achieved`, e — só quando há prazo futuro e o objetivo não está atingido — `months_until_deadline` (dias até ao prazo / 30, arredondado para cima) e `required_monthly_contribution` (`remaining / meses`, **arredondado para cima** com `ROUND_UP` para que contribuir esse valor chegue mesmo ao alvo). Se o prazo já passou e não foi atingido, `deadline_passed = true`.
- **Porquê não "ao teu ritmo de poupança atinges isto em <data>"**: essa projeção precisaria da poupança mensal média (do dashboard), que é a poupança *total* — dividi-la por vários objetivos não está modelado e daria uma data enganadora se tiver 3 metas. A projeção orientada ao prazo é determinística, por-objetivo, e honesta.

**Decisão — PATCH e o prazo nullable**: os outros `*Update` do projeto tratam `None` como "não mexer". Para o prazo isso impediria de o remover depois de definido. O router usa **`"deadline" in payload.model_fields_set`** para distinguir: enviar `{"deadline": null}` limpa o prazo, omitir o campo mantém-no. É a forma correta em Pydantic v2 e vale a pena saber explicar.

**Detalhe — normalização decimal**: quando `current_amount` vem do default Pydantic (`Decimal("0")`) e não de um round-trip à BD, ainda não tem casas fixas — o `_to_read` faz `.quantize("0.01")` a `target`/`current`/`remaining` para a API ser sempre `"0.00"`, não `"0"` (mesmo padrão do dashboard e dos orçamentos).

**Camadas**: `models/goal.py`, `schemas/goal.py`, `repositories/goal_repository.py`, `services/goal_service.py`, `api/v1/goals.py` (`GET`, `POST`, `PATCH /{id}`, `POST /{id}/contributions`, `DELETE /{id}`).
- Testes (`tests/api/test_goals.py`, 14 testes): criar mínimo, alvo ≤ 0 → 422, `required_monthly_contribution` com prazo (900/3 = 300), arredondamento para cima (1000/3 → 333.34), objetivo atingido não tem contribuição exigida, prazo ultrapassado sinalizado, contribuir soma, contribuir até atingir, contribuir para negativo → 422, editar campos, **limpar o prazo com `{"deadline": null}` e mantê-lo ao omitir**, eliminar, isolamento entre utilizadores, exige autenticação. **116 testes no total**, `ruff` limpo.

**Frontend**: `features/goals/` (`types.ts`, `api.ts`, `schemas.ts` zod) + `src/routes/goals.tsx` (rota `/objetivos`): formulário RHF+zod (nome, alvo, já poupado opcional, prazo opcional), e uma lista com barra de progresso (índigo a encher; **verde** quando atingido), nota de prazo contextual ("Poupa €Y/mês nos próximos Z meses (até <data>)" / "Prazo ultrapassado" / "🎉 Objetivo atingido" / "Sem prazo definido"), campo de contribuição inline ("Adicionar"), editar inline e eliminar com confirmação. Link "Objetivos" no dashboard.

**Validei end-to-end no browser real**:
1. "Fundo de emergência" alvo 3000 €, já poupado 500 € → barra a 17%, "Sem prazo definido", "Faltam 2500,00 €".
2. "Ferias" alvo 1200 €, prazo 25/11/2026 (hoje 27/08) → "**Poupa 400,00 €/mês nos próximos 3 meses (até 2026-11-25)**".
3. Contribuir 1200 € para "Ferias" → barra **verde** a 100%, "🎉 Objetivo atingido" (nota de prazo e "Faltam" desaparecem).
4. Editei "Fundo de emergência" a adicionar prazo 27/02/2027 → recalcula: "**Poupa 357,15 €/mês nos próximos 7 meses**" (2500/7, arredondado para cima).

Apaguei o utilizador de teste no fim.

---

## 2026-08-27 — Fase 11: Monthly History & Analytics (comparação + evolução)

**Objetivo**: navegar entre meses e ver como o mês se compara com o anterior (variação de receitas/despesas/poupança) e a evolução dos últimos meses num gráfico.

**Decisão — módulo `analytics` separado, só leitura, sem tabela**: os dados já existem nas `transactions`; a analytics é agregação por pedido, como o dashboard (Fase 6). Não estendi o `dashboard_service` para não o inchar — `analytics_service` reutiliza diretamente o `dashboard_repository.sum_amount_by_type` (que já recebe uma lista de `user_id` e um intervalo de datas).

**Decisão — analytics é sempre da vista individual**: o toggle "Agregado familiar" vive no dashboard (Fase 7). Estender a comparação/evolução ao agregado seria mais superfície de teste sem valor claro para a defesa — fica anotado como iteração futura possível.

**Refactor — `app/core/dates.add_months(day, n)`**: aritmética de meses absolutos (`ano*12 + mês` ± `n`), devolve sempre o dia 1. Usado para "mês anterior" na comparação e para gerar a janela de N meses da evolução. Reescrevi o `month_bounds` em função dele (uma linha). Testes unitários novos em `tests/unit/test_dates.py` (viragem de ano nos dois sentidos, normalização para dia 1).

**Backend**:
- `schemas/analytics.py` — `MonthTotals` (mês + receitas/despesas/poupança), `MonthComparison` (current + previous + `*_change` absolutos + `*_change_pct` — `None` quando o mês anterior foi 0, para não dividir por zero), `MonthlyTrend` (lista de `MonthTotals`, do mais antigo para o mais recente).
- `services/analytics_service.py` — `get_comparison` e `get_trend`. A % de variação é `(atual − anterior) / |anterior| * 100`, arredondada a 1 casa.
- `api/v1/analytics.py` — `GET /analytics/monthly-comparison?month=` e `GET /analytics/monthly-trend?months=6&month=` (`months` validado `2..24` pelo FastAPI → `422` fora do intervalo).
- Testes (`tests/api/test_analytics.py`, 6 testes + 6 unit de datas): deltas e percentagens corretos, sem dados no mês anterior → `pct = None`, série de N meses ordenada e com os meses vazios a `0.00`, `months` fora do intervalo → 422, isolamento entre utilizadores, exige autenticação. **128 testes no total**, `ruff` limpo.

**Frontend**:
- `src/lib/month.ts` ganhou `parseIsoDate` (sem o desvio de fuso de `new Date(string)`) e `shortMonthLabel` ("2026-06-01" → "jun 26", com ano de 2 dígitos porque a série pode cruzar o ano).
- `features/analytics/` (`types.ts`, `api.ts`) + `src/routes/history.tsx` (rota `/historico`): navegação por mês, cartão "Comparação com o mês anterior" com 3 linhas (Receitas/Despesas/Poupança) — cada uma mostra o valor atual e a variação com seta ▲/▼ e **cor que depende da direção "boa"**: receitas/poupança a subir = verde, despesas a subir = vermelho, e vice-versa. Gráfico "Evolução dos últimos 6 meses" = `ComposedChart` do Recharts (barras verdes de receitas + barras vermelhas de despesas + linha índigo de poupança), com `YAxis hide` para o Recharts calcular a escala corretamente com séries mistas barra+linha.
- Link "Histórico" no dashboard.

**Validei end-to-end no browser real** (5 meses de dados, abr–ago 2026):
- Agosto (2200 receitas / 1400 despesas): "Receitas 2200,00 € ▲ 400,00 € (+22.2%)" verde, "Despesas 1400,00 € ▼ 500,00 € (-26.3%)" verde, "Poupança 800,00 € ▲ 900,00 €" verde (mês anterior tinha poupança negativa).
- Recuei para Julho (1800 / 1900): "Receitas ▼ 200,00 € (-10%)" vermelho, "Despesas ▲ 250,00 € (+15.2%)" vermelho, "Poupança -100,00 € ▼ 450,00 €" vermelho.
- Gráfico: barras dimensionadas corretamente, linha de poupança a mergulhar abaixo de zero em julho e a subir em agosto, eixo X com os meses certos, mês sem dados sem barra.

Apaguei o utilizador de teste no fim.

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

**Validei end-to-end no browser real**: utilizador com receita 2500 €/mês, orçamento Casa 200 € (gasto 250 → 125%), orçamento Lazer 100 € (gasto 85 → 85%), despesas do mês (335 €) muito abaixo do mês anterior (1400 €), e um objetivo "Carro" 10 000 € com prazo a 45 dias.
- Mês atual: 5 alertas na ordem certa — 3 avisos (Casa ultrapassado 125%, Lazer quase no limite 85%, "Carro pode não chegar a tempo — precisas de 5 000,00 €/mês e este mês poupaste 2 165,00 €") seguidos de 2 positivos ("Despesas 76% abaixo do mês anterior", "Boa taxa de poupança — 86.6% das receitas").
- Recuei para julho: só 1 alerta ("Gastaste mais do que ganhaste este mês — -1 400,00 €"); os alertas de objetivo desaparecem (só contam no mês atual), e não há alertas de orçamento (os orçamentos são de agosto).

Apaguei o utilizador de teste no fim.

---

## 2026-08-27 — Fase 13 (parte 1): testes de segurança + endurecimento

**Objetivo**: provar que os riscos clássicos de uma API que mexe em dinheiro estão cobertos — SQL injection, acesso aos dados de outro utilizador, bypass de autenticação, vazamento de segredos — e corrigir o que os testes revelassem.

**Reorganização**: mudei a fixture `client` de `tests/api/conftest.py` para `tests/conftest.py` (raiz), ao lado do `db_session`, para ficar disponível também ao novo pacote `tests/security/`. Nenhum teste existente mudou de comportamento.

**`tests/security/test_sql_injection.py` (8 testes)** — o projeto usa sempre o ORM com queries parametrizadas (`select().where(Coluna == valor)`), nunca concatenação de strings SQL. Os testes injetam 9 payloads clássicos (`'; DROP TABLE users; --`, `' OR '1'='1`, `UNION SELECT password_hash ...`, etc.) em **todos** os campos de texto controlados pelo utilizador (nome de categoria/conta/objetivo/agregado, descrição de transação, email de login) e nos parâmetros de query (`type`, `account_id`, `date_from`, `scope`), e verifico: (a) o payload é guardado/devolvido **literalmente** (é dado, não código); (b) o "canário" (uma categoria criada antes) continua lá; (c) nenhum hash bcrypt (`$2b$`) aparece na resposta; (d) tipos fortes nos parâmetros → `422`, nunca execução; (e) depois de uma rajada de tentativas, a app continua 100% funcional (novo registo + login).

**`tests/security/test_authorization.py` (9 testes)** — IDOR consolidado: para **cada** recurso (contas, categorias, transações, orçamentos, objetivos, recorrências, agregados), o utilizador B não vê, não edita e não elimina os objetos de A — mesmo com o id exato — e recebe **`404`, não `403`** (a escolha da secção 8: não confirmar sequer que o id existe). Inclui: B não cria uma transação que referencie a conta/categoria de A; C não aceita nem cancela um convite de agregado dirigido a B.

**`tests/security/test_authentication.py` (8 testes)** — 14 endpoints protegidos exigem token; headers `Authorization` malformados → `401`; token assinado com a chave errada → `401`; **`alg: none`** (token sem assinatura) → `401`; token expirado → `401`; assinatura válida mas `sub` de utilizador inexistente → `401`; assinatura válida mas `sub` não-UUID / em falta → **`401` (não `500`)**.
- **Correção em `app/api/deps.py`**: `uuid.UUID(payload["sub"])` podia levantar `ValueError`/`KeyError` não apanhado → `500` com stack trace. Só um token assinado com a minha chave chega a esse ponto, mas se a chave vazasse (ou houvesse um bug interno) o modo de falha tem de ser um `401` limpo. Passou a apanhar `(jwt.InvalidTokenError, KeyError, ValueError, TypeError)`.

**`tests/security/test_data_exposure.py` (6 testes)** — `password`/`password_hash` nunca aparecem em nenhuma resposta (verificação recursiva) nem qualquer `$2b$`; o refresh token é guardado **como hash SHA-256** (64 hex), nunca em claro (verificado direto na tabela `refresh_tokens`); o cookie de refresh tem `HttpOnly` + `SameSite=lax` + `Path=/api/v1/auth` + `Max-Age`; o erro de login é **idêntico** para "email não existe" e "password errada" (sem enumeração de contas); um `404` não devolve stack trace nem menciona `sqlalchemy`.

**`tests/security/test_input_hardening.py` (6 testes)** — valores que a BD rejeitaria são apanhados com `422` antes do insert, nunca `500`:
- **Endurecimento nos schemas**: `Field(max_digits=12, decimal_places=2)` em todos os campos monetários (conta, transação, orçamento, objetivo, contribuição, recorrência) — `NUMERIC(12,2)` overflow ou 3 casas decimais → `422`. `max_length` nos campos de texto que não o tinham (nome de categoria/conta = 100, descrição de transação = 200, `icon`/`color`) — strings gigantes → `422`.
- Montantes ≤ 0 em campos `gt=0` → `422`. **Mass-assignment**: campos extra no corpo (`user_id`, `id`, `current_balance`) são ignorados pelo Pydantic — a conta criada é do autor, com id gerado pelo servidor e `current_balance == initial_balance`. JSON malformado → `422`.

**Resultado**: **178 testes a passar** (141 → 178), `ruff` limpo. Smoke test contra o servidor a correr (registo/login/dashboard OK; overflow → 422; token inválido → 401) e verificação visual no browser de que o dashboard continua a funcionar depois do endurecimento. Nenhuma alteração ao frontend (as validações de comprimento no cliente ficam para o polish da Fase 16).

**Gaps de segurança que assumi (fora do âmbito do projeto, a mencionar na defesa se perguntado)**: sem rate limiting / proteção de força bruta no login; sem CSRF token explícito (mitigado por `SameSite=lax` + o access token ir no header `Authorization`, não num cookie); sem cabeçalhos de segurança HTTP (HSTS, CSP) — esses são responsabilidade da camada de deployment (Fase 15).

---

## 2026-08-27 — Fase 13 (parte 2): endurecimento, CI, e testes de casos-limite

Revisão transversal do projeto (segurança, funcionamento, Docker, CI). O que corrigi/melhorei:

**Autenticação — deteção de reutilização de refresh token (resposta a roubo)**: antes, apresentar um refresh token já rodado dava só um `401`. Agora, se o token existe mas está revogado, assumo roubo e **revogo toda a família de tokens do utilizador** (`refresh_token_repository.revoke_all_for_user`), obrigando a novo login em todo o lado — nem o token legítimo mais recente sobrevive. O router de `/refresh` passou a fazer `db.commit()` também no caminho de erro, para a revogação em massa ficar persistida. Teste novo em `test_auth.py`; confirmei também com um smoke test contra o servidor a correr.

**Config — `SECRET_KEY` à prova de erro**: `config.py` ganhou validadores Pydantic — a chave tem de ter ≥ 32 caracteres (RFC 7518) em qualquer ambiente, e fora de `development` a app recusa-se a arrancar se a chave contiver marcadores de placeholder (`change`, `example`, `placeholder`, …). Propriedade `settings.is_production` (`environment` não é `development`/`dev`/`local`/`test`). O `.env.example` passou a ter um `SECRET_KEY` que funciona em dev mas falha em produção, e o README explica como gerar um real. 5 testes unitários em `tests/unit/test_config.py`.

**Robustez de ligação à BD**: `create_engine(..., pool_pre_ping=True)` — cada ligação do pool é testada antes de ser usada, para não rebentar com "connection already closed" se o Postgres reiniciar (ex: `docker compose restart postgres`).

**Docker**:
- `.dockerignore` no `backend/` e no `frontend/` — o contexto de build deixou de enviar `node_modules`/`.venv`/`.env`/`dist`/`.git`. No frontend isto elimina um risco real: o `COPY . .` do Dockerfile trazia o `node_modules` do host (Windows) para dentro da imagem Linux, por cima do `npm ci`.
- Healthcheck no serviço `backend` do `docker-compose.yml` (faz `GET /health` a cada 10s), e o `frontend` passou a `depends_on: backend: condition: service_healthy` — `docker compose up` só dá o frontend por pronto depois de a API responder. Validei: `backend running healthy`.

**CI — `.github/workflows/ci.yml` cresceu de 2 para 6 jobs** (era "Fase 0: só lint"): `lint-backend`, `lint-frontend`, **`test-backend`** (com `services: postgres` real, `alembic upgrade head`, `pytest`), **`build-frontend`** (`tsc + vite build`), **`build-images`** (`docker build` dos dois Dockerfiles, para os validar). É essencialmente a Fase 14 adiantada. Testei os dois `docker build` localmente e passam.

**Testes de casos-limite (`tests/api/test_edge_cases.py`, 6 testes)**: eliminar a conta que é *destino* de uma transferência → `409` (a FK `destination_account_id` também é RESTRICT, não só `account_id`); transação num mês muito no futuro (2030-12) não conta no mês atual mas conta em dezembro/2030 e já move o saldo global (aritmética de mês na fronteira do ano); converter uma transação `EXPENSE` → `TRANSFER` limpa a categoria e reaplica os saldos corretamente; transferência sem conta de destino → `422`; último membro a sair de um agregado leva os convites pendentes em cascata; o parâmetro `month` do dashboard aceita qualquer dia do mês.

**Resultado**: **190 testes a passar** (178 → 190), `ruff` limpo, `docker compose config` válido, os dois `docker build` a passar, backend `healthy`.

### Melhorias que identifiquei e que ainda faltam (backlog priorizado)

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
