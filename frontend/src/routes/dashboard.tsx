import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { AnimatedNumber } from '@/components/animated-number'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import * as accountsApi from '@/features/accounts/api'
import { CardStatus } from '@/features/accounts/card-status'
import { ACCOUNT_TYPE_ICONS } from '@/features/accounts/icons'
import type { Account } from '@/features/accounts/types'
import { CATEGORY_COLOR_PALETTE } from '@/features/categories/types'
import { getDashboard } from '@/features/dashboard/api'
import type { CategoryExpense, DashboardScope } from '@/features/dashboard/types'
import * as goalsApi from '@/features/goals/api'
import type { Goal } from '@/features/goals/types'
import { getMyHousehold } from '@/features/households/api'
import { getInsights } from '@/features/insights/api'
import type { Insight, InsightSeverity } from '@/features/insights/types'
import * as recurringApi from '@/features/recurring/api'
import { merchantBadge } from '@/features/recurring/merchant-icons'
import type { RecurringExpense } from '@/features/recurring/types'
import {
  addMonths,
  daysUntil,
  isSameMonth,
  monthLabel,
  shortDayMonthLabel,
  startOfMonth,
  toIsoDate,
} from '@/lib/month'
import { useAuth } from '@/features/auth/use-auth'

// Paleta de recurso para categorias sem cor escolhida na página de Categorias
// (mesma paleta do seletor de cor, para ficarem visualmente coerentes).
const FALLBACK_COLORS = CATEGORY_COLOR_PALETTE

function formatMoney(value: string | number, currency: string) {
  return new Intl.NumberFormat('pt-PT', { style: 'currency', currency }).format(Number(value))
}

function colorFor(item: CategoryExpense, index: number) {
  return item.color ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length]
}

const INSIGHT_STYLES: Record<InsightSeverity, { dot: string; symbol: string }> = {
  warning: { dot: 'bg-amber-500', symbol: '!' },
  info: { dot: 'bg-sky-500', symbol: 'i' },
  positive: { dot: 'bg-emerald-500', symbol: '✓' },
}

function AccountCard({ account, currency, index }: { account: Account; currency: string; index: number }) {
  const reduceMotion = useReducedMotion()
  const Icon = ACCOUNT_TYPE_ICONS[account.type]
  const negative = Number(account.current_balance) < 0

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05, ease: 'easeOut' }}
      whileHover={reduceMotion ? undefined : { y: -2 }}
      className="flex flex-col gap-3 rounded-2xl border border-border bg-surface-raised p-4 transition-shadow hover:shadow-md"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent-strong dark:text-accent">
          <Icon className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm text-ink-muted">{account.name}</p>
          <p className={`text-lg font-semibold tabular-nums ${negative ? 'text-red-500' : 'text-ink'}`}>
            <AnimatedNumber
              value={Number(account.current_balance)}
              formatter={(v) => formatMoney(v, currency)}
            />
          </p>
        </div>
      </div>
      <CardStatus account={account} currency={currency} formatMoney={formatMoney} />
    </motion.div>
  )
}

function AccountsSummaryCard({ accounts, currency }: { accounts: Account[]; currency: string }) {
  if (accounts.length === 0) {
    return null
  }

  return (
    <div>
      <h2 className="mb-3 text-sm font-medium text-ink-muted">As tuas contas</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {accounts.map((account, index) => (
          <AccountCard key={account.id} account={account} currency={currency} index={index} />
        ))}
      </div>
    </div>
  )
}

function InsightsCard({ insights }: { insights: Insight[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">CentiSible Insights</CardTitle>
      </CardHeader>
      <CardContent>
        {insights.length === 0 ? (
          <p className="text-sm text-ink-muted">Sem alertas este mês — está tudo em ordem.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {insights.map((insight, index) => {
              const style = INSIGHT_STYLES[insight.severity]
              return (
                <li key={`${insight.rule}-${index}`} className="flex gap-3">
                  <span
                    className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${style.dot}`}
                  >
                    {style.symbol}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-ink">{insight.title}</p>
                    <p className="text-sm text-ink-muted">{insight.detail}</p>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}

// Conteúdo puro (sem <Card> à volta) — partilhado entre o cartão "Objetivos"
// do desktop e o separador "Objetivos" da vista compacta em mobile (ver
// MobileSecondaryTabs), que não pode meter um <Card> dentro doutro <Card>.
function GoalsList({ goals, currency }: { goals: Goal[]; currency: string }) {
  const reduceMotion = useReducedMotion()
  // Os já atingidos vão para o fim — os que ainda precisam de atenção são o
  // que vale a pena ver de relance no painel.
  const sorted = [...goals].sort((a, b) => Number(a.is_achieved) - Number(b.is_achieved))
  const shown = sorted.slice(0, 3)

  if (shown.length === 0) {
    return (
      <p className="text-sm text-ink-muted">
        Ainda não tens objetivos.{' '}
        <Link to="/objetivos" className="text-ink underline">
          Cria o primeiro
        </Link>
        .
      </p>
    )
  }

  return (
    <ul className="flex flex-col gap-4">
      {shown.map((goal, index) => {
        const clamped = Math.min(goal.progress_percentage, 100)
        return (
          <li key={goal.id} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="truncate text-ink">{goal.name}</span>
              <span className="shrink-0 tabular-nums text-ink-muted">
                <AnimatedNumber
                  value={Number(goal.current_amount)}
                  formatter={(v) => formatMoney(v, currency)}
                />{' '}
                de {formatMoney(goal.target_amount, currency)}
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
              <motion.div
                className={`h-full rounded-full ${goal.is_achieved ? 'bg-emerald-500' : 'bg-accent'}`}
                initial={reduceMotion ? false : { width: 0 }}
                animate={{ width: `${clamped}%` }}
                transition={{
                  duration: reduceMotion ? 0 : 0.6,
                  delay: reduceMotion ? 0 : index * 0.1,
                  ease: 'easeOut',
                }}
              />
            </div>
          </li>
        )
      })}
    </ul>
  )
}

function GoalsSummaryCard({ goals, currency }: { goals: Goal[]; currency: string }) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-base">Objetivos</CardTitle>
        <Link to="/objetivos" className="text-sm text-ink-muted underline hover:text-ink">
          Ver todos
        </Link>
      </CardHeader>
      <CardContent>
        <GoalsList goals={goals} currency={currency} />
      </CardContent>
    </Card>
  )
}

const UPCOMING_WINDOW_DAYS = 30

function UpcomingPaymentsCard({
  items,
  currency,
}: {
  items: RecurringExpense[]
  currency: string
}) {
  const upcoming = items
    .filter((item) => item.active && daysUntil(item.next_occurrence) <= UPCOMING_WINDOW_DAYS)
    .sort((a, b) => a.next_occurrence.localeCompare(b.next_occurrence))
  const total = upcoming.reduce((sum, item) => sum + Number(item.amount), 0)

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-base">Próximos pagamentos</CardTitle>
        <Link to="/recorrentes" className="text-sm text-ink-muted underline hover:text-ink">
          Ver todos
        </Link>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {upcoming.length === 0 ? (
          <p className="text-sm text-ink-muted">
            Sem pagamentos agendados nos próximos {UPCOMING_WINDOW_DAYS} dias.
          </p>
        ) : (
          <>
            <ul className="flex flex-col gap-3">
              {upcoming.slice(0, 5).map((item) => {
                const badge = merchantBadge(item.description)
                const Icon = badge.icon
                const overdue = daysUntil(item.next_occurrence) < 0
                return (
                  <li key={item.id} className="flex items-center gap-3">
                    <span
                      className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white"
                      style={{ backgroundColor: badge.color }}
                    >
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-ink">{item.description}</p>
                      <p className={`text-xs ${overdue ? 'font-medium text-red-500' : 'text-ink-muted'}`}>
                        {overdue ? 'Em atraso' : shortDayMonthLabel(item.next_occurrence)}
                      </p>
                    </div>
                    <span className="shrink-0 text-sm font-semibold tabular-nums text-ink">
                      {formatMoney(item.amount, currency)}
                    </span>
                  </li>
                )
              })}
            </ul>
            <div className="flex items-center justify-between border-t border-border pt-3 text-sm">
              <span className="text-ink-muted">Total (próx. {UPCOMING_WINDOW_DAYS} dias)</span>
              <span className="font-semibold tabular-nums text-ink">
                {formatMoney(total, currency)}
              </span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function StatCard({
  label,
  value,
  currency,
  hint,
  tone,
  index,
}: {
  label: string
  value: number
  currency: string
  hint?: string
  tone?: 'positive' | 'negative'
  index: number
}) {
  const reduceMotion = useReducedMotion()
  const valueColor =
    tone === 'positive' ? 'text-emerald-500' : tone === 'negative' ? 'text-red-500' : 'text-ink'

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05, ease: 'easeOut' }}
      whileHover={reduceMotion ? undefined : { y: -2 }}
    >
      <Card className="transition-shadow hover:shadow-md">
        <CardContent className="flex flex-col gap-1 p-5">
          <span className="text-sm text-ink-muted">{label}</span>
          <span className={`text-2xl font-semibold tabular-nums ${valueColor}`}>
            <AnimatedNumber value={value} formatter={(v) => formatMoney(v, currency)} />
          </span>
          {hint && <span className="text-xs text-ink-subtle">{hint}</span>}
        </CardContent>
      </Card>
    </motion.div>
  )
}

function ExpensesByCategory({
  items,
  currency,
}: {
  items: CategoryExpense[]
  currency: string
}) {
  const total = items.reduce((sum, item) => sum + Number(item.total), 0)

  if (items.length === 0) {
    return <p className="p-6 text-sm text-ink-muted">Sem despesas registadas neste mês.</p>
  }

  const chartData = items.map((item, index) => ({
    // `category_id` sozinho não é único aqui — uma despesa partilhada e a
    // pessoal de uma pessoa podem ter vindo da mesma categoria original (o
    // backend escolhe um id representativo com `min()`) — por isso a chave
    // junta também o dono, para nunca colidir entre duas linhas.
    key: `${item.category_id}:${item.owner_name ?? ''}`,
    name: item.owner_name ? `${item.name} · ${item.owner_name}` : item.name,
    value: Number(item.total),
    color: colorFor(item, index),
  }))

  return (
    <div className="grid grid-cols-1 gap-6 p-6 sm:grid-cols-2">
      <div className="h-64 xl:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius="55%"
              outerRadius="85%"
              paddingAngle={2}
              stroke="none"
            >
              {chartData.map((entry) => (
                <Cell key={entry.key} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => formatMoney(Number(value), currency)}
              contentStyle={{
                borderRadius: 8,
                border: '1px solid var(--border)',
                background: 'var(--surface-raised)',
                color: 'var(--ink)',
                fontSize: 13,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <ul className="flex flex-col justify-center gap-3">
        {chartData.map((entry) => {
          const percentage = total > 0 ? Math.round((entry.value / total) * 100) : 0
          return (
            <li key={entry.key} className="flex flex-col gap-1.5 text-sm">
              <span className="flex items-center justify-between gap-3">
                <span className="flex items-center gap-2 text-ink">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: entry.color }}
                  />
                  {entry.name}
                </span>
                <span className="tabular-nums text-ink-muted">
                  {formatMoney(entry.value, currency)} · {percentage}%
                </span>
              </span>
              <span className="h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
                <span
                  className="block h-full rounded-full"
                  style={{ width: `${percentage}%`, backgroundColor: entry.color }}
                />
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

// Em mobile, "Despesas por categoria" e "Objetivos" são conteúdo para
// explorar com calma — ao contrário de Insights/Próximos pagamentos, não são
// urgentes. Em vez de mais scroll, ficam atrás de um separador simples
// (mesmo estilo do seletor Individual/Agregado já usado no painel).
function MobileSecondaryTabs({
  expensesItems,
  goals,
  currency,
}: {
  expensesItems: CategoryExpense[]
  goals: Goal[]
  currency: string
}) {
  const [tab, setTab] = useState<'despesas' | 'objetivos'>('despesas')

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-base">
          {tab === 'despesas' ? 'Despesas por categoria' : 'Objetivos'}
        </CardTitle>
        <div className="flex rounded-lg border border-border p-0.5 text-sm">
          {(['despesas', 'objetivos'] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setTab(option)}
              className={`rounded-md px-3 py-1 transition-colors ${
                tab === option
                  ? 'bg-accent text-accent-foreground'
                  : 'text-ink-muted hover:text-ink'
              }`}
            >
              {option === 'despesas' ? 'Despesas' : 'Objetivos'}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className={tab === 'despesas' ? 'p-0' : undefined}>
        {tab === 'despesas' ? (
          <ExpensesByCategory items={expensesItems} currency={currency} />
        ) : (
          <GoalsList goals={goals} currency={currency} />
        )}
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const firstName = user?.name?.split(' ')[0] ?? ''

  const currentMonth = useMemo(() => startOfMonth(new Date()), [])
  const [month, setMonth] = useState(currentMonth)
  const isCurrentMonth = isSameMonth(month, currentMonth)
  const [scope, setScope] = useState<DashboardScope>('individual')

  const { data: household } = useQuery({ queryKey: ['household'], queryFn: getMyHousehold })
  const hasHousehold = Boolean(household)
  // Se o utilizador saiu do agregado enquanto via a vista partilhada, volta a "individual".
  const effectiveScope: DashboardScope = hasHousehold ? scope : 'individual'

  // `placeholderData: keepPreviousData` — ao trocar de mês/vista, mantém o
  // resumo anterior visível (com `isFetching` a assinalar a atualização em
  // curso) em vez de o ecrã ficar em branco até o novo mês chegar; é essa
  // troca súbita que parecia um "piscar" ao navegar.
  const {
    data,
    isLoading,
    isFetching,
    isError,
  } = useQuery({
    queryKey: ['dashboard', toIsoDate(month), effectiveScope],
    queryFn: () => getDashboard(toIsoDate(month), effectiveScope),
    placeholderData: keepPreviousData,
  })

  // Alertas são sempre da vista individual (conselhos pessoais).
  const { data: insights } = useQuery({
    queryKey: ['insights', toIsoDate(month)],
    queryFn: () => getInsights(toIsoDate(month)),
    placeholderData: keepPreviousData,
  })

  // Objetivos não têm mês/agregado — são sempre os do próprio utilizador,
  // a mesma chave de query usada em routes/goals.tsx (a cache é partilhada).
  const { data: goals } = useQuery({ queryKey: ['goals'], queryFn: goalsApi.listGoals })

  // Saldos por conta — sem mês/agregado, mesma chave de routes/accounts.tsx.
  const { data: accounts } = useQuery({ queryKey: ['accounts'], queryFn: accountsApi.listAccounts })

  // Próximos pagamentos: sem mês/agregado, mesma chave de routes/recurring.tsx.
  const { data: recurring } = useQuery({
    queryKey: ['recurring'],
    queryFn: recurringApi.listRecurring,
  })

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-[2000px] flex-col gap-6 p-4 py-10 xl:p-10">
      <PageHeader title={`Olá, ${firstName}`} subtitle="Aqui está o resumo do teu mês." />

      {accounts && <AccountsSummaryCard accounts={accounts} currency={currency} />}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setMonth((m) => addMonths(m, -1))}>
            ‹
          </Button>
          <span className="min-w-40 text-center text-sm font-medium text-ink">
            {monthLabel(month)}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={isCurrentMonth}
            onClick={() => setMonth((m) => addMonths(m, 1))}
          >
            ›
          </Button>
          {!isCurrentMonth && (
            <Button variant="ghost" size="sm" onClick={() => setMonth(currentMonth)}>
              Mês atual
            </Button>
          )}
        </div>

        {hasHousehold && (
          <div className="flex rounded-lg border border-border p-0.5 text-sm">
            {(['individual', 'household'] as const).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setScope(option)}
                className={`rounded-md px-3 py-1 transition-colors ${
                  effectiveScope === option
                    ? 'bg-accent text-accent-foreground'
                    : 'text-ink-muted hover:text-ink'
                }`}
              >
                {option === 'individual' ? 'Individual' : 'Agregado familiar'}
              </button>
            ))}
          </div>
        )}
      </div>

      {isLoading && <p className="text-sm text-ink-muted">A carregar o resumo...</p>}
      {isError && <p className="text-sm text-red-600">Não foi possível carregar o resumo do mês.</p>}

      {data && (
        <div
          className={`flex flex-col gap-6 transition-opacity duration-300 ${isFetching ? 'opacity-60' : 'opacity-100'}`}
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              index={0}
              label="Saldo global"
              value={Number(data.total_balance)}
              currency={currency}
              hint="Soma de todas as contas, agora"
            />
            <StatCard
              index={1}
              label="Receitas do mês"
              value={Number(data.total_income)}
              currency={currency}
              tone="positive"
            />
            <StatCard
              index={2}
              label="Despesas do mês"
              value={Number(data.total_expenses)}
              currency={currency}
              tone="negative"
            />
            <StatCard
              index={3}
              label="Poupança do mês"
              value={Number(data.net)}
              currency={currency}
              tone={Number(data.net) < 0 ? 'negative' : 'positive'}
              hint={
                data.savings_rate === null
                  ? 'Sem receitas este mês'
                  : `${data.savings_rate}% das receitas`
              }
            />
            {data.scope === 'household' && (
              <StatCard
                index={4}
                label="Despesas partilhadas"
                value={Number(data.shared_expenses_total)}
                currency={currency}
                hint={
                  Number(data.total_expenses) > 0
                    ? `${Math.round((Number(data.shared_expenses_total) / Number(data.total_expenses)) * 100)}% do total`
                    : 'Sem despesas este mês'
                }
              />
            )}
          </div>

          {/* Desktop (xl+): duas linhas de dois cartões — mantém tudo
              genericamente do mesmo tamanho dentro de cada linha (o gráfico +
              Insights são naturalmente mais "cheios" que Objetivos + Próximos
              pagamentos, por isso ficam juntos numa linha à parte). */}
          <div className="hidden flex-col gap-6 xl:flex">
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Despesas por categoria</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <ExpensesByCategory items={data.expenses_by_category} currency={currency} />
                </CardContent>
              </Card>

              {insights && <InsightsCard insights={insights} />}
            </div>

            <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
              {goals && <GoalsSummaryCard goals={goals} currency={currency} />}
              <UpcomingPaymentsCard items={recurring ?? []} currency={currency} />
            </div>
          </div>

          {/* Mobile: o que é urgente (alertas, próximos pagamentos) primeiro
              — antes, ficava tudo lá em baixo, depois do gráfico e dos
              objetivos, o que não era prático. O gráfico e os objetivos, mais
              para "explorar com calma", passam a um separador em vez de mais
              scroll (ver MobileSecondaryTabs). */}
          <div className="flex flex-col gap-6 xl:hidden">
            {insights && <InsightsCard insights={insights} />}
            <UpcomingPaymentsCard items={recurring ?? []} currency={currency} />
            <MobileSecondaryTabs
              expensesItems={data.expenses_by_category}
              goals={goals ?? []}
              currency={currency}
            />
          </div>
        </div>
      )}
    </main>
  )
}
