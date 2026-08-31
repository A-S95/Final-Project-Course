import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { errorMessage } from '@/api/client'
import { AnimatedListItem } from '@/components/animated-list-item'
import { AnimatedNumber } from '@/components/animated-number'
import { PageHeader } from '@/components/page-header'
import { QueryError } from '@/components/query-error'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/features/auth/use-auth'
import * as goalsApi from '@/features/goals/api'
import { goalSchema, type GoalFormValues } from '@/features/goals/schemas'
import type { Goal, GoalInput } from '@/features/goals/types'
import { AMOUNT_RE, formatMoney } from '@/lib/money'

const EMPTY_VALUES: GoalFormValues = {
  name: '',
  target_amount: '',
  current_amount: '',
  deadline: '',
}

function toFormValues(goal: Goal): GoalFormValues {
  return {
    name: goal.name,
    target_amount: goal.target_amount,
    current_amount: goal.current_amount,
    deadline: goal.deadline ?? '',
  }
}

function toInput(values: GoalFormValues): GoalInput {
  return {
    name: values.name,
    target_amount: values.target_amount,
    current_amount: values.current_amount || '0',
    deadline: values.deadline || null,
  }
}

function GoalForm({
  defaultValues,
  onSubmit,
  onCancel,
  submitLabel,
}: {
  defaultValues: GoalFormValues
  onSubmit: (values: GoalFormValues) => Promise<void>
  onCancel?: () => void
  submitLabel: string
}) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<GoalFormValues>({ resolver: zodResolver(goalSchema), defaultValues })

  const submit = async (values: GoalFormValues) => {
    setFormError(null)
    try {
      await onSubmit(values)
    } catch (err) {
      setFormError(errorMessage(err, 'Não foi possível guardar o objetivo.'))
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="name">Nome</Label>
          <Input id="name" autoComplete="off" {...register('name')} />
          {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="target_amount">Objetivo</Label>
          <Input id="target_amount" inputMode="decimal" {...register('target_amount')} />
          {errors.target_amount && (
            <p className="text-sm text-red-600">{errors.target_amount.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="current_amount">Já poupado (opcional)</Label>
          <Input
            id="current_amount"
            inputMode="decimal"
            placeholder="0.00"
            {...register('current_amount')}
          />
          {errors.current_amount && (
            <p className="text-sm text-red-600">{errors.current_amount.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="deadline">Prazo (opcional)</Label>
          <Input id="deadline" type="date" {...register('deadline')} />
        </div>
      </div>

      {formError && <p className="text-sm text-red-600">{formError}</p>}

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'A guardar...' : submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
        )}
      </div>
    </form>
  )
}

function GoalProgress({ goal }: { goal: Goal }) {
  const reduceMotion = useReducedMotion()
  const clamped = Math.min(goal.progress_percentage, 100)
  const color = goal.is_achieved ? 'bg-emerald-500' : 'bg-accent'
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

function GoalDeadlineNote({ goal, currency }: { goal: Goal; currency: string }) {
  if (goal.is_achieved) {
    return <span className="text-sm text-emerald-500">🎉 Objetivo atingido</span>
  }
  if (goal.deadline_passed) {
    return <span className="text-sm text-red-500">Prazo ultrapassado ({goal.deadline})</span>
  }
  if (goal.required_monthly_contribution && goal.months_until_deadline) {
    return (
      <span className="text-sm text-ink-muted">
        Poupa {formatMoney(goal.required_monthly_contribution, currency)}/mês nos próximos{' '}
        {goal.months_until_deadline} meses (até {goal.deadline})
      </span>
    )
  }
  return <span className="text-sm text-ink-muted">Sem prazo definido</span>
}

function ContributeForm({ goal }: { goal: Goal }) {
  const queryClient = useQueryClient()
  const [amount, setAmount] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => goalsApi.contributeToGoal(goal.id, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      setAmount('')
    },
    onError: (err) => setError(errorMessage(err, 'Não foi possível registar a contribuição.')),
  })

  return (
    <form
      className="flex items-center gap-2"
      onSubmit={(e) => {
        e.preventDefault()
        setError(null)
        if (AMOUNT_RE.test(amount)) mutation.mutate()
      }}
    >
      <Input
        className="h-8 w-28"
        inputMode="decimal"
        placeholder="0.00"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <Button size="sm" type="submit" disabled={!AMOUNT_RE.test(amount) || mutation.isPending}>
        Adicionar
      </Button>
      {error && <span className="text-sm text-red-600">{error}</span>}
    </form>
  )
}

function GoalRow({ goal, currency, index }: { goal: Goal; currency: string; index: number }) {
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: (values: GoalFormValues) => goalsApi.updateGoal(goal.id, toInput(values)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      setIsEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => goalsApi.deleteGoal(goal.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['goals'] }),
    onError: (err) => {
      setDeleteError(errorMessage(err, 'Não foi possível eliminar o objetivo.'))
      setConfirmingDelete(false)
    },
  })

  if (isEditing) {
    return (
      <Card className="p-5">
        <GoalForm
          defaultValues={toFormValues(goal)}
          submitLabel="Guardar"
          onCancel={() => setIsEditing(false)}
          onSubmit={(values) => updateMutation.mutateAsync(values).then(() => undefined)}
        />
      </Card>
    )
  }

  return (
    <AnimatedListItem
      index={index}
      className="flex flex-col gap-3 rounded-2xl border border-border bg-surface-raised p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-medium text-ink">{goal.name}</span>
        <span className="text-sm tabular-nums text-ink-muted">
          <AnimatedNumber
            value={Number(goal.current_amount)}
            formatter={(v) => formatMoney(v, currency)}
          />{' '}
          de {formatMoney(goal.target_amount, currency)} ·{' '}
          <AnimatedNumber value={goal.progress_percentage} formatter={(v) => `${Math.round(v)}%`} />
        </span>
      </div>

      <GoalProgress goal={goal} />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-0.5">
          <GoalDeadlineNote goal={goal} currency={currency} />
          {!goal.is_achieved && (
            <span className="text-xs tabular-nums text-ink-subtle">
              Faltam{' '}
              <AnimatedNumber
                value={Number(goal.remaining)}
                formatter={(v) => formatMoney(v, currency)}
              />
            </span>
          )}
        </div>

        {confirmingDelete ? (
          <div className="flex items-center gap-2">
            <span className="text-sm text-ink-muted">Eliminar?</span>
            <Button
              variant="destructive"
              size="sm"
              disabled={deleteMutation.isPending}
              onClick={() => deleteMutation.mutate()}
            >
              Confirmar
            </Button>
            <Button variant="outline" size="sm" onClick={() => setConfirmingDelete(false)}>
              Cancelar
            </Button>
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <ContributeForm goal={goal} />
            <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
              Editar
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setDeleteError(null)
                setConfirmingDelete(true)
              }}
            >
              Eliminar
            </Button>
          </div>
        )}
      </div>

      {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}
    </AnimatedListItem>
  )
}

export function GoalsPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)

  const {
    data: goals,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['goals'], queryFn: goalsApi.listGoals })

  const createMutation = useMutation({
    mutationFn: (values: GoalFormValues) => goalsApi.createGoal(toInput(values)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      setIsCreating(false)
    },
  })

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-[2200px] flex-col gap-6 p-4 py-10 xl:p-10">
      <PageHeader title="Objetivos" />

      <div className="flex flex-col gap-6 lg:flex-row-reverse lg:items-start lg:gap-8">
        <div className="w-full shrink-0 lg:sticky lg:top-10 lg:w-80">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Novo objetivo</CardTitle>
            </CardHeader>
            <CardContent>
              {isCreating ? (
                <GoalForm
                  defaultValues={EMPTY_VALUES}
                  submitLabel="Criar objetivo"
                  onCancel={() => setIsCreating(false)}
                  onSubmit={(values) => createMutation.mutateAsync(values).then(() => undefined)}
                />
              ) : (
                <Button onClick={() => setIsCreating(true)}>Adicionar objetivo</Button>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="min-w-0 flex-1">
          {isLoading && <p className="text-sm text-ink-muted">A carregar...</p>}
          {isError && (
            <QueryError message="Não foi possível carregar os objetivos." onRetry={() => refetch()} />
          )}
          {goals && goals.length === 0 && (
            <Card className="p-6 text-sm text-ink-muted">Ainda não tens objetivos.</Card>
          )}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {goals?.map((goal, index) => (
              <GoalRow key={goal.id} goal={goal} currency={currency} index={index} />
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
