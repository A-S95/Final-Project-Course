import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useMemo, useState } from 'react'
import { errorMessage } from '@/api/client'
import { AnimatedListItem } from '@/components/animated-list-item'
import { AnimatedNumber } from '@/components/animated-number'
import { PageHeader } from '@/components/page-header'
import { QueryError } from '@/components/query-error'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { useAuth } from '@/features/auth/use-auth'
import * as budgetsApi from '@/features/budgets/api'
import type { Budget } from '@/features/budgets/types'
import * as categoriesApi from '@/features/categories/api'
import { addMonths, isSameMonth, monthLabel, startOfMonth, toIsoDate } from '@/lib/month'
import { AMOUNT_RE, formatMoney } from '@/lib/money'

function ProgressBar({ percentage }: { percentage: number }) {
  const reduceMotion = useReducedMotion()
  const clamped = Math.min(percentage, 100)
  const color =
    percentage > 100 ? 'bg-red-500' : percentage >= 80 ? 'bg-amber-500' : 'bg-emerald-500'
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-surface-hover">
      <motion.div
        className={`h-full rounded-full ${color}`}
        initial={reduceMotion ? false : { width: 0 }}
        animate={{ width: `${clamped}%` }}
        transition={{ duration: reduceMotion ? 0 : 0.6, ease: 'easeOut' }}
      />
    </div>
  )
}

function BudgetRow({
  budget,
  currency,
  index,
}: {
  budget: Budget
  currency: string
  index: number
}) {
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [amount, setAmount] = useState(budget.amount)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: () => budgetsApi.updateBudget(budget.id, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
      setEditing(false)
    },
    onError: (err) => setError(errorMessage(err, 'Não foi possível guardar o orçamento.')),
  })

  const deleteMutation = useMutation({
    mutationFn: () => budgetsApi.deleteBudget(budget.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['budgets'] }),
    onError: (err) => setError(errorMessage(err, 'Não foi possível eliminar o orçamento.')),
  })

  const over = Number(budget.remaining) < 0

  return (
    <AnimatedListItem
      index={index}
      className="flex flex-col gap-3 rounded-2xl border border-border bg-surface-raised p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-medium text-ink">{budget.category_name}</span>
        <span className="text-sm tabular-nums text-ink-muted">
          <AnimatedNumber value={Number(budget.spent)} formatter={(v) => formatMoney(v, currency)} />
          {' / '}
          {formatMoney(budget.amount, currency)} ·{' '}
          <AnimatedNumber value={budget.percentage} formatter={(v) => `${Math.round(v)}%`} />
        </span>
      </div>

      <ProgressBar percentage={budget.percentage} />

      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className={`text-sm tabular-nums ${over ? 'text-red-500' : 'text-ink-muted'}`}>
          <AnimatedNumber
            value={Math.abs(Number(budget.remaining))}
            formatter={(v) => formatMoney(v, currency)}
          />{' '}
          {over ? 'acima do orçamento' : 'disponível'}
        </span>

        {editing ? (
          <div className="flex items-center gap-2">
            <Input
              className="h-8 w-28"
              inputMode="decimal"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <Button
              size="sm"
              disabled={!AMOUNT_RE.test(amount) || updateMutation.isPending}
              onClick={() => {
                setError(null)
                updateMutation.mutate()
              }}
            >
              Guardar
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setAmount(budget.amount)
                setEditing(false)
              }}
            >
              Cancelar
            </Button>
          </div>
        ) : confirmingDelete ? (
          <div className="flex items-center gap-2">
            <span className="text-sm text-ink-muted">Eliminar?</span>
            <Button
              size="sm"
              variant="destructive"
              disabled={deleteMutation.isPending}
              onClick={() => deleteMutation.mutate()}
            >
              Confirmar
            </Button>
            <Button size="sm" variant="outline" onClick={() => setConfirmingDelete(false)}>
              Cancelar
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Button size="sm" variant="outline" onClick={() => setEditing(true)}>
              Editar valor
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setConfirmingDelete(true)}>
              Eliminar
            </Button>
          </div>
        )}
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </AnimatedListItem>
  )
}

function NewBudgetForm({
  month,
  availableCategories,
}: {
  month: Date
  availableCategories: { id: string; name: string }[]
}) {
  const queryClient = useQueryClient()
  const [categoryId, setCategoryId] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState<string | null>(null)

  const createMutation = useMutation({
    mutationFn: () =>
      budgetsApi.createBudget({
        category_id: categoryId,
        period_month: toIsoDate(month),
        amount,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
      setCategoryId('')
      setAmount('')
    },
    onError: (err) => setError(errorMessage(err, 'Não foi possível criar o orçamento.')),
  })

  const canSubmit = categoryId !== '' && AMOUNT_RE.test(amount)

  if (availableCategories.length === 0) {
    return (
      <p className="text-sm text-ink-muted">
        Todas as categorias de despesa já têm orçamento para este mês.
      </p>
    )
  }

  return (
    <form
      className="flex flex-col gap-3"
      onSubmit={(e) => {
        e.preventDefault()
        setError(null)
        if (canSubmit) createMutation.mutate()
      }}
    >
      <div className="flex flex-col gap-3">
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="budget-category">Categoria</Label>
          <Select
            id="budget-category"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
          >
            <option value="">Escolhe uma categoria</option>
            {availableCategories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="budget-amount">Valor mensal</Label>
          <Input
            id="budget-amount"
            inputMode="decimal"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={!canSubmit || createMutation.isPending}>
          {createMutation.isPending ? 'A criar...' : 'Adicionar'}
        </Button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  )
}

export function BudgetsPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'

  const currentMonth = useMemo(() => startOfMonth(new Date()), [])
  const [month, setMonth] = useState(currentMonth)
  const isCurrentMonth = isSameMonth(month, currentMonth)

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.listCategories,
  })
  const {
    data: budgets,
    isLoading,
    isFetching,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['budgets', toIsoDate(month)],
    queryFn: () => budgetsApi.listBudgets(toIsoDate(month)),
    placeholderData: keepPreviousData,
  })

  const availableCategories = useMemo(() => {
    const budgeted = new Set((budgets ?? []).map((b) => b.category_id))
    return (categories ?? [])
      .filter((c) => c.type === 'EXPENSE' && !budgeted.has(c.id))
      .map((c) => ({ id: c.id, name: c.name }))
  }, [categories, budgets])

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-[2200px] flex-col gap-6 p-4 py-10 xl:p-10">
      <PageHeader title="Orçamentos" />

      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => setMonth((m) => addMonths(m, -1))}>
          ‹
        </Button>
        <span className="min-w-40 text-center text-sm font-medium text-ink">
          {monthLabel(month)}
        </span>
        <Button variant="outline" size="sm" onClick={() => setMonth((m) => addMonths(m, 1))}>
          ›
        </Button>
        {!isCurrentMonth && (
          <Button variant="ghost" size="sm" onClick={() => setMonth(currentMonth)}>
            Mês atual
          </Button>
        )}
      </div>

      <div className="flex flex-col gap-6 lg:flex-row-reverse lg:items-start lg:gap-8">
        <div className="w-full shrink-0 lg:sticky lg:top-10 lg:w-80">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Novo orçamento</CardTitle>
            </CardHeader>
            <CardContent>
              <NewBudgetForm month={month} availableCategories={availableCategories} />
            </CardContent>
          </Card>
        </div>

        <div className="min-w-0 flex-1">
          {isLoading && <p className="text-sm text-ink-muted">A carregar...</p>}
          {isError && (
            <QueryError
              message="Não foi possível carregar os orçamentos."
              onRetry={() => refetch()}
            />
          )}
          {budgets && budgets.length === 0 && (
            <Card className="p-6 text-sm text-ink-muted">Sem orçamentos para este mês.</Card>
          )}
          <div
            className={`grid grid-cols-1 gap-4 transition-opacity duration-300 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 ${isFetching ? 'opacity-60' : 'opacity-100'}`}
          >
            {budgets?.map((budget, index) => (
              <BudgetRow key={budget.id} budget={budget} currency={currency} index={index} />
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
