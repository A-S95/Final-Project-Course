import { useQuery } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useMemo, useState } from 'react'
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import * as analyticsApi from '@/features/analytics/api'
import type { MonthComparison } from '@/features/analytics/types'
import { useAuth } from '@/features/auth/use-auth'
import {
  addMonths,
  isSameMonth,
  monthLabel,
  shortMonthLabel,
  startOfMonth,
  toIsoDate,
} from '@/lib/month'

function formatMoney(value: string | number, currency: string) {
  return new Intl.NumberFormat('pt-PT', { style: 'currency', currency }).format(Number(value))
}

function ChangeRow({
  label,
  current,
  change,
  pct,
  currency,
  goodDirection,
  index,
}: {
  label: string
  current: string
  change: string
  pct: number | null
  currency: string
  goodDirection: 'up' | 'down'
  index: number
}) {
  const reduceMotion = useReducedMotion()
  const delta = Number(change)
  const isFlat = delta === 0
  const isGood = isFlat || (delta > 0 ? goodDirection === 'up' : goodDirection === 'down')
  const color = isFlat ? 'text-ink-muted' : isGood ? 'text-emerald-500' : 'text-red-500'
  const arrow = isFlat ? '' : delta > 0 ? '▲' : '▼'
  const pctText = pct === null ? '' : ` (${pct > 0 ? '+' : ''}${pct}%)`

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.08, ease: 'easeOut' }}
      className="flex items-center justify-between gap-3 border-b border-border py-3 last:border-0"
    >
      <span className="text-sm text-ink-muted">{label}</span>
      <div className="flex items-center gap-3 text-sm">
        <span className="tabular-nums font-medium text-ink">{formatMoney(current, currency)}</span>
        <span className={`tabular-nums ${color}`}>
          {isFlat
            ? 'sem variação'
            : `${arrow} ${formatMoney(Math.abs(delta), currency)}${pctText}`}
        </span>
      </div>
    </motion.div>
  )
}

function ComparisonCard({
  comparison,
  currency,
}: {
  comparison: MonthComparison
  currency: string
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Comparação com o mês anterior</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col">
        <ChangeRow
          index={0}
          label="Receitas"
          current={comparison.current.total_income}
          change={comparison.income_change}
          pct={comparison.income_change_pct}
          currency={currency}
          goodDirection="up"
        />
        <ChangeRow
          index={1}
          label="Despesas"
          current={comparison.current.total_expenses}
          change={comparison.expenses_change}
          pct={comparison.expenses_change_pct}
          currency={currency}
          goodDirection="down"
        />
        <ChangeRow
          index={2}
          label="Poupança"
          current={comparison.current.net}
          change={comparison.net_change}
          pct={null}
          currency={currency}
          goodDirection="up"
        />
      </CardContent>
    </Card>
  )
}

export function HistoryPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'

  const currentMonth = useMemo(() => startOfMonth(new Date()), [])
  const [month, setMonth] = useState(currentMonth)
  const isCurrentMonth = isSameMonth(month, currentMonth)
  const isoMonth = toIsoDate(month)

  const {
    data: comparison,
    isLoading: isComparisonLoading,
    isError: isComparisonError,
  } = useQuery({
    queryKey: ['analytics-comparison', isoMonth],
    queryFn: () => analyticsApi.getMonthlyComparison(isoMonth),
  })
  const {
    data: trend,
    isLoading: isTrendLoading,
    isError: isTrendError,
  } = useQuery({
    queryKey: ['analytics-trend', isoMonth],
    queryFn: () => analyticsApi.getMonthlyTrend(isoMonth, 6),
  })

  const chartData = (trend?.points ?? []).map((point) => ({
    label: shortMonthLabel(point.month),
    Receitas: Number(point.total_income),
    Despesas: Number(point.total_expenses),
    Poupança: Number(point.net),
  }))

  return (
    <main className="mx-auto flex min-h-svh max-w-3xl flex-col gap-6 p-4 py-10">
      <PageHeader title="Histórico mensal" />

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

      {isComparisonLoading && (
        <p className="text-sm text-ink-muted">A carregar...</p>
      )}
      {isComparisonError && (
        <p className="text-sm text-red-600">Não foi possível carregar a comparação mensal.</p>
      )}
      {comparison && <ComparisonCard comparison={comparison} currency={currency} />}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Evolução dos últimos 6 meses</CardTitle>
        </CardHeader>
        <CardContent>
          {isTrendLoading && (
            <p className="p-6 text-sm text-ink-muted">A carregar...</p>
          )}
          {isTrendError && (
            <p className="p-6 text-sm text-red-600">
              Não foi possível carregar a evolução mensal.
            </p>
          )}
          {trend && (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 12, fill: 'var(--ink-muted)' }} />
                <YAxis hide />
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
                <Legend wrapperStyle={{ fontSize: 12, color: 'var(--ink-muted)' }} />
                <Bar dataKey="Receitas" fill="#10b981" radius={[3, 3, 0, 0]} maxBarSize={28} />
                <Bar dataKey="Despesas" fill="#ef4444" radius={[3, 3, 0, 0]} maxBarSize={28} />
                <Line
                  dataKey="Poupança"
                  stroke="var(--accent)"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  type="monotone"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
