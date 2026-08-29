import { useQuery } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CATEGORY_COLOR_PALETTE } from '@/features/categories/types'
import { getDashboard } from '@/features/dashboard/api'
import type { CategoryExpense, DashboardScope } from '@/features/dashboard/types'
import { getMyHousehold } from '@/features/households/api'
import { getInsights } from '@/features/insights/api'
import type { Insight, InsightSeverity } from '@/features/insights/types'
import { addMonths, isSameMonth, monthLabel, startOfMonth, toIsoDate } from '@/lib/month'
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

function InsightsCard({ insights }: { insights: Insight[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Alertas do mês</CardTitle>
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

function StatCard({
  label,
  value,
  hint,
  tone,
  index,
}: {
  label: string
  value: string
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
    >
      <Card>
        <CardContent className="flex flex-col gap-1 p-5">
          <span className="text-sm text-ink-muted">{label}</span>
          <span className={`text-2xl font-semibold tabular-nums ${valueColor}`}>{value}</span>
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
    name: item.name,
    value: Number(item.total),
    color: colorFor(item, index),
  }))

  return (
    <div className="grid grid-cols-1 gap-6 p-6 sm:grid-cols-2">
      <div className="h-56">
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
                <Cell key={entry.name} fill={entry.color} />
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

      <ul className="flex flex-col justify-center gap-2">
        {chartData.map((entry) => {
          const percentage = total > 0 ? Math.round((entry.value / total) * 100) : 0
          return (
            <li key={entry.name} className="flex items-center justify-between gap-3 text-sm">
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
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export function DashboardPage() {
  const { user, logout } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const reduceMotion = useReducedMotion()

  const currentMonth = useMemo(() => startOfMonth(new Date()), [])
  const [month, setMonth] = useState(currentMonth)
  const isCurrentMonth = isSameMonth(month, currentMonth)
  const [scope, setScope] = useState<DashboardScope>('individual')

  const { data: household } = useQuery({ queryKey: ['household'], queryFn: getMyHousehold })
  const hasHousehold = Boolean(household)
  // Se o utilizador saiu do agregado enquanto via a vista partilhada, volta a "individual".
  const effectiveScope: DashboardScope = hasHousehold ? scope : 'individual'

  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard', toIsoDate(month), effectiveScope],
    queryFn: () => getDashboard(toIsoDate(month), effectiveScope),
  })

  // Alertas são sempre da vista individual (conselhos pessoais).
  const { data: insights } = useQuery({
    queryKey: ['insights', toIsoDate(month)],
    queryFn: () => getInsights(toIsoDate(month)),
  })

  return (
    <main className="mx-auto flex min-h-svh max-w-5xl flex-col gap-6 p-4 py-10">
      <motion.header
        initial={reduceMotion ? false : { opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="flex flex-wrap items-center justify-between gap-4"
      >
        <div>
          <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">
            FinTrack
          </h1>
          <p className="text-sm text-ink-muted">Olá, {user?.name}</p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <nav className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
            <Link to="/contas" className="text-ink-muted underline hover:text-ink">
              Contas
            </Link>
            <Link to="/categorias" className="text-ink-muted underline hover:text-ink">
              Categorias
            </Link>
            <Link to="/transacoes" className="text-ink-muted underline hover:text-ink">
              Transações
            </Link>
            <Link to="/orcamentos" className="text-ink-muted underline hover:text-ink">
              Orçamentos
            </Link>
            <Link to="/historico" className="text-ink-muted underline hover:text-ink">
              Histórico
            </Link>
            <Link to="/recorrentes" className="text-ink-muted underline hover:text-ink">
              Recorrentes
            </Link>
            <Link to="/objetivos" className="text-ink-muted underline hover:text-ink">
              Objetivos
            </Link>
            <Link to="/agregado" className="text-ink-muted underline hover:text-ink">
              Agregado
            </Link>
            <Link to="/definicoes" className="text-ink-muted underline hover:text-ink">
              Definições
            </Link>
          </nav>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="outline" size="sm" onClick={() => logout()}>
              Terminar sessão
            </Button>
          </div>
        </div>
      </motion.header>

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
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              index={0}
              label="Saldo global"
              value={formatMoney(data.total_balance, currency)}
            />
            <StatCard
              index={1}
              label="Receitas do mês"
              value={formatMoney(data.total_income, currency)}
              tone="positive"
            />
            <StatCard
              index={2}
              label="Despesas do mês"
              value={formatMoney(data.total_expenses, currency)}
              tone="negative"
            />
            <StatCard
              index={3}
              label="Poupança do mês"
              value={formatMoney(data.net, currency)}
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
                value={formatMoney(data.shared_expenses_total, currency)}
                hint={
                  Number(data.total_expenses) > 0
                    ? `${Math.round((Number(data.shared_expenses_total) / Number(data.total_expenses)) * 100)}% do total`
                    : 'Sem despesas este mês'
                }
              />
            )}
          </div>

          {insights && <InsightsCard insights={insights} />}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Despesas por categoria</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ExpensesByCategory items={data.expenses_by_category} currency={currency} />
            </CardContent>
          </Card>
        </>
      )}
    </main>
  )
}
