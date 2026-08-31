import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { errorMessage } from '@/api/client'
import { AnimatedListItem } from '@/components/animated-list-item'
import { PageHeader } from '@/components/page-header'
import { QueryError } from '@/components/query-error'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import * as accountsApi from '@/features/accounts/api'
import type { Account } from '@/features/accounts/types'
import { useAuth } from '@/features/auth/use-auth'
import * as categoriesApi from '@/features/categories/api'
import type { Category } from '@/features/categories/types'
import * as recurringApi from '@/features/recurring/api'
import { recurringSchema, type RecurringFormValues } from '@/features/recurring/schemas'
import {
  FREQUENCY_LABELS,
  RECURRING_FREQUENCIES,
  type RecurringExpense,
} from '@/features/recurring/types'
import { formatMoney } from '@/lib/money'

const today = () => new Date().toISOString().slice(0, 10)

const EMPTY_VALUES: RecurringFormValues = {
  account_id: '',
  category_id: '',
  description: '',
  amount: '',
  frequency: 'MONTHLY',
  next_occurrence: today(),
  active: true,
}

function toFormValues(recurring: RecurringExpense): RecurringFormValues {
  return {
    account_id: recurring.account_id,
    category_id: recurring.category_id,
    description: recurring.description,
    amount: recurring.amount,
    frequency: recurring.frequency,
    next_occurrence: recurring.next_occurrence,
    active: recurring.active,
  }
}

function RecurringForm({
  accounts,
  categories,
  defaultValues,
  onSubmit,
  onCancel,
  submitLabel,
}: {
  accounts: Account[]
  categories: Category[]
  defaultValues: RecurringFormValues
  onSubmit: (values: RecurringFormValues) => Promise<void>
  onCancel?: () => void
  submitLabel: string
}) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RecurringFormValues>({ resolver: zodResolver(recurringSchema), defaultValues })

  const submit = async (values: RecurringFormValues) => {
    setFormError(null)
    try {
      await onSubmit(values)
    } catch (err) {
      setFormError(errorMessage(err, 'Não foi possível guardar a despesa recorrente.'))
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="description">Descrição</Label>
          <Input id="description" autoComplete="off" {...register('description')} />
          {errors.description && (
            <p className="text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="amount">Valor</Label>
          <Input id="amount" inputMode="decimal" {...register('amount')} />
          {errors.amount && <p className="text-sm text-red-600">{errors.amount.message}</p>}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="account_id">Conta</Label>
          <Select id="account_id" {...register('account_id')}>
            <option value="">Escolhe uma conta</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.name}
              </option>
            ))}
          </Select>
          {errors.account_id && <p className="text-sm text-red-600">{errors.account_id.message}</p>}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="category_id">Categoria</Label>
          <Select id="category_id" {...register('category_id')}>
            <option value="">Escolhe uma categoria</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Select>
          {errors.category_id && (
            <p className="text-sm text-red-600">{errors.category_id.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="frequency">Frequência</Label>
          <Select id="frequency" {...register('frequency')}>
            {RECURRING_FREQUENCIES.map((f) => (
              <option key={f} value={f}>
                {FREQUENCY_LABELS[f]}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="next_occurrence">Próxima ocorrência</Label>
          <Input id="next_occurrence" type="date" {...register('next_occurrence')} />
          {errors.next_occurrence && (
            <p className="text-sm text-red-600">{errors.next_occurrence.message}</p>
          )}
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" className="h-4 w-4" {...register('active')} />
        Ativa (entra na geração automática de transações)
      </label>

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

function RecurringRow({
  recurring,
  accounts,
  categories,
  currency,
  index,
}: {
  recurring: RecurringExpense
  accounts: Account[]
  categories: Category[]
  currency: string
  index: number
}) {
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['recurring'] })
  }

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<RecurringFormValues>) =>
      recurringApi.updateRecurring(recurring.id, payload),
    onSuccess: () => {
      invalidate()
      setIsEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => recurringApi.deleteRecurring(recurring.id),
    onSuccess: invalidate,
    onError: (err) => {
      setDeleteError(errorMessage(err, 'Não foi possível eliminar a recorrência.'))
      setConfirmingDelete(false)
    },
  })

  if (isEditing) {
    return (
      <Card className="p-5">
        <RecurringForm
          accounts={accounts}
          categories={categories}
          defaultValues={toFormValues(recurring)}
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
      <div>
        <p className="font-medium text-ink">
          {recurring.description}
          {recurring.is_due && (
            <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-400">
              Em atraso
            </span>
          )}
          {!recurring.active && (
            <span className="ml-2 rounded-full bg-surface-hover px-2 py-0.5 text-xs text-ink-muted">
              Pausada
            </span>
          )}
        </p>
        <p className="text-sm text-ink-muted">
          {FREQUENCY_LABELS[recurring.frequency]} · dia {recurring.day_of_month} · próxima:{' '}
          {recurring.next_occurrence} · {recurring.account_name} · {recurring.category_name}
        </p>
      </div>

      <span className="text-2xl font-semibold tabular-nums text-red-500">
        {formatMoney(recurring.amount, currency)}
      </span>

      <div className="flex flex-wrap items-center gap-2 border-t border-border pt-3">
        {confirmingDelete ? (
          <>
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
          </>
        ) : (
          <>
            <Button
              variant="outline"
              size="sm"
              disabled={updateMutation.isPending}
              onClick={() => updateMutation.mutate({ active: !recurring.active })}
            >
              {recurring.active ? 'Pausar' : 'Retomar'}
            </Button>
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
          </>
        )}
      </div>

      {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}
    </AnimatedListItem>
  )
}

export function RecurringPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [generateResult, setGenerateResult] = useState<{ text: string; error?: boolean } | null>(
    null,
  )

  const { data: accounts } = useQuery({ queryKey: ['accounts'], queryFn: accountsApi.listAccounts })
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.listCategories,
  })
  const {
    data: recurring,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['recurring'], queryFn: recurringApi.listRecurring })

  const accountsList = accounts ?? []
  const expenseCategories = (categories ?? []).filter((c) => c.type === 'EXPENSE')
  const canCreate = accountsList.length > 0 && expenseCategories.length > 0
  const dueCount = (recurring ?? []).filter((r) => r.is_due).length

  const createMutation = useMutation({
    mutationFn: (values: RecurringFormValues) => recurringApi.createRecurring(values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recurring'] })
      setIsCreating(false)
    },
  })

  const generateMutation = useMutation({
    mutationFn: recurringApi.generateRecurring,
    onSuccess: (result) => {
      for (const key of [['recurring'], ['transactions'], ['accounts'], ['budgets'], ['dashboard']]) {
        queryClient.invalidateQueries({ queryKey: key })
      }
      setGenerateResult({
        text:
          result.generated === 0
            ? 'Nada a gerar — está tudo em dia.'
            : `${result.generated} transação(ões) gerada(s).`,
      })
    },
    onError: (err) => {
      setGenerateResult({
        text: errorMessage(err, 'Não foi possível gerar as transações.'),
        error: true,
      })
    },
  })

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-[2200px] flex-col gap-6 p-4 py-10 xl:p-10">
      <PageHeader title="Despesas recorrentes" />

      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-3 p-5">
          <div className="text-sm">
            <p className="font-medium">Gerar transações em falta</p>
            <p className="text-ink-muted">
              {dueCount > 0
                ? `${dueCount} recorrência(s) com ocorrências por lançar.`
                : 'Cria as transações das recorrências vencidas.'}
            </p>
          </div>
          <Button
            disabled={generateMutation.isPending}
            onClick={() => {
              setGenerateResult(null)
              generateMutation.mutate()
            }}
          >
            {generateMutation.isPending ? 'A gerar...' : 'Gerar agora'}
          </Button>
        </CardContent>
        {generateResult && (
          <p
            className={`px-5 pb-4 text-sm ${generateResult.error ? 'text-red-600' : 'text-ink-muted'}`}
          >
            {generateResult.text}
          </p>
        )}
      </Card>

      <div className="flex flex-col gap-6 lg:flex-row-reverse lg:items-start lg:gap-8">
        <div className="w-full shrink-0 lg:sticky lg:top-10 lg:w-80">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Nova despesa recorrente</CardTitle>
            </CardHeader>
            <CardContent>
              {!canCreate ? (
                <p className="text-sm text-ink-muted">
                  Precisas de pelo menos uma conta e uma categoria de despesa.
                </p>
              ) : isCreating ? (
                <RecurringForm
                  accounts={accountsList}
                  categories={expenseCategories}
                  defaultValues={EMPTY_VALUES}
                  submitLabel="Criar"
                  onCancel={() => setIsCreating(false)}
                  onSubmit={(values) => createMutation.mutateAsync(values).then(() => undefined)}
                />
              ) : (
                <Button onClick={() => setIsCreating(true)}>Adicionar recorrência</Button>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="min-w-0 flex-1">
          {isLoading && <p className="text-sm text-ink-muted">A carregar...</p>}
          {isError && (
            <QueryError
              message="Não foi possível carregar as recorrências."
              onRetry={() => refetch()}
            />
          )}
          {recurring && recurring.length === 0 && (
            <Card className="p-6 text-sm text-ink-muted">
              Ainda não tens despesas recorrentes.
            </Card>
          )}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {recurring?.map((item, index) => (
              <RecurringRow
                key={item.id}
                recurring={item}
                accounts={accountsList}
                categories={expenseCategories}
                currency={currency}
                index={index}
              />
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
