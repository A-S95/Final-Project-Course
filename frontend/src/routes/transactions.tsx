import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useMemo, useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { ApiError } from '@/api/client'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import * as accountsApi from '@/features/accounts/api'
import type { Account } from '@/features/accounts/types'
import * as categoriesApi from '@/features/categories/api'
import type { Category } from '@/features/categories/types'
import * as transactionsApi from '@/features/transactions/api'
import { useAuth } from '@/features/auth/use-auth'
import { getMyHousehold } from '@/features/households/api'
import { transactionSchema, type TransactionFormValues } from '@/features/transactions/schemas'
import {
  TRANSACTION_TYPE_LABELS,
  TRANSACTION_TYPES,
  type Transaction,
  type TransactionFilters,
} from '@/features/transactions/types'

const EMPTY_VALUES: TransactionFormValues = {
  account_id: '',
  destination_account_id: '',
  category_id: '',
  type: 'EXPENSE',
  amount: '',
  description: '',
  date: new Date().toISOString().slice(0, 10),
  is_shared: false,
}

function transactionToFormValues(transaction: Transaction): TransactionFormValues {
  return {
    account_id: transaction.account_id,
    destination_account_id: transaction.destination_account_id ?? '',
    category_id: transaction.category_id ?? '',
    type: transaction.type,
    amount: transaction.amount,
    description: transaction.description ?? '',
    date: transaction.date,
    is_shared: transaction.is_shared,
  }
}

function formValuesToInput(values: TransactionFormValues) {
  return {
    account_id: values.account_id,
    destination_account_id: values.type === 'TRANSFER' ? values.destination_account_id : null,
    category_id: values.type === 'TRANSFER' ? null : values.category_id,
    type: values.type,
    amount: values.amount,
    description: values.description || null,
    date: values.date,
    is_shared: values.type === 'EXPENSE' ? values.is_shared : false,
  }
}

function TransactionForm({
  accounts,
  categories,
  hasHousehold,
  defaultValues,
  onSubmit,
  onCancel,
  submitLabel,
}: {
  accounts: Account[]
  categories: Category[]
  hasHousehold: boolean
  defaultValues: TransactionFormValues
  onSubmit: (values: TransactionFormValues) => Promise<void>
  onCancel?: () => void
  submitLabel: string
}) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<TransactionFormValues>({ resolver: zodResolver(transactionSchema), defaultValues })

  const type = useWatch({ control, name: 'type' })
  const accountId = useWatch({ control, name: 'account_id' })
  const categoriesForType = categories.filter((c) => c.type === type)

  const submit = async (values: TransactionFormValues) => {
    setFormError(null)
    try {
      await onSubmit(values)
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Não foi possível guardar a transação.')
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="type">Tipo</Label>
          <Select id="type" {...register('type')}>
            {TRANSACTION_TYPES.map((t) => (
              <option key={t} value={t}>
                {TRANSACTION_TYPE_LABELS[t]}
              </option>
            ))}
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="account_id">{type === 'TRANSFER' ? 'Conta de origem' : 'Conta'}</Label>
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

        {type === 'TRANSFER' ? (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="destination_account_id">Conta de destino</Label>
            <Select id="destination_account_id" {...register('destination_account_id')}>
              <option value="">Escolhe uma conta</option>
              {accounts
                .filter((account) => account.id !== accountId)
                .map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name}
                  </option>
                ))}
            </Select>
            {errors.destination_account_id && (
              <p className="text-sm text-red-600">{errors.destination_account_id.message}</p>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="category_id">Categoria</Label>
            <Select id="category_id" {...register('category_id')}>
              <option value="">Escolhe uma categoria</option>
              {categoriesForType.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </Select>
            {errors.category_id && (
              <p className="text-sm text-red-600">{errors.category_id.message}</p>
            )}
          </div>
        )}

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="amount">Valor</Label>
          <Input id="amount" inputMode="decimal" {...register('amount')} />
          {errors.amount && <p className="text-sm text-red-600">{errors.amount.message}</p>}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="date">Data</Label>
          <Input id="date" type="date" {...register('date')} />
          {errors.date && <p className="text-sm text-red-600">{errors.date.message}</p>}
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="description">Descrição (opcional)</Label>
          <Input id="description" autoComplete="off" {...register('description')} />
        </div>
      </div>

      {hasHousehold && type === 'EXPENSE' && (
        <label htmlFor="is_shared" className="flex items-center gap-2 text-sm">
          <input
            id="is_shared"
            type="checkbox"
            className="h-4 w-4 rounded border-border-strong"
            {...register('is_shared')}
          />
          Despesa partilhada com o agregado (ex: renda, contas da casa)
        </label>
      )}

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

function formatMoney(value: string, currency: string) {
  return new Intl.NumberFormat('pt-PT', { style: 'currency', currency }).format(Number(value))
}

function TransactionRow({
  transaction,
  accounts,
  categories,
  hasHousehold,
  accountsById,
  categoriesById,
  currency,
  index,
}: {
  transaction: Transaction
  accounts: Account[]
  categories: Category[]
  hasHousehold: boolean
  accountsById: Map<string, Account>
  categoriesById: Map<string, Category>
  currency: string
  index: number
}) {
  const reduceMotion = useReducedMotion()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)

  const updateMutation = useMutation({
    mutationFn: (values: TransactionFormValues) =>
      transactionsApi.updateTransaction(transaction.id, formValuesToInput(values)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      setIsEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => transactionsApi.deleteTransaction(transaction.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
    },
  })

  if (isEditing) {
    return (
      <div className="border-b border-border p-4 last:border-0">
        <TransactionForm
          accounts={accounts}
          categories={categories}
          hasHousehold={hasHousehold}
          defaultValues={transactionToFormValues(transaction)}
          submitLabel="Guardar"
          onCancel={() => setIsEditing(false)}
          onSubmit={(values) => updateMutation.mutateAsync(values).then(() => undefined)}
        />
      </div>
    )
  }

  const account = accountsById.get(transaction.account_id)
  const destination = transaction.destination_account_id
    ? accountsById.get(transaction.destination_account_id)
    : null
  const category = transaction.category_id ? categoriesById.get(transaction.category_id) : null

  const sign = transaction.type === 'EXPENSE' ? '-' : transaction.type === 'INCOME' ? '+' : ''
  const amountColor =
    transaction.type === 'EXPENSE'
      ? 'text-red-500'
      : transaction.type === 'INCOME'
        ? 'text-emerald-500'
        : 'text-ink-muted'

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.03, ease: 'easeOut' }}
      className="flex flex-wrap items-center justify-between gap-3 border-b border-border p-4 last:border-0"
    >
      <div>
        <p className="flex items-center gap-2 font-medium text-ink">
          {transaction.description || TRANSACTION_TYPE_LABELS[transaction.type]}
          {transaction.is_shared && (
            <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-normal text-accent-strong dark:text-accent">
              Partilhada
            </span>
          )}
        </p>
        <p className="text-sm text-ink-muted">
          {transaction.date} ·{' '}
          {transaction.type === 'TRANSFER'
            ? `${account?.name ?? '?'} → ${destination?.name ?? '?'}`
            : `${account?.name ?? '?'} · ${category?.name ?? '?'}`}
        </p>
      </div>
      <div className="flex items-center gap-4">
        <p className={`text-lg font-semibold tabular-nums ${amountColor}`}>
          {sign}
          {formatMoney(transaction.amount, currency)}
        </p>
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
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
              Editar
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setConfirmingDelete(true)}>
              Eliminar
            </Button>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export function TransactionsPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [filters, setFilters] = useState<TransactionFilters>({})

  const { data: accounts } = useQuery({ queryKey: ['accounts'], queryFn: accountsApi.listAccounts })
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.listCategories,
  })
  const { data: household } = useQuery({ queryKey: ['household'], queryFn: getMyHousehold })
  const hasHousehold = Boolean(household)
  const {
    data: transactions,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => transactionsApi.listTransactions(filters),
  })

  const accountsById = useMemo(
    () => new Map((accounts ?? []).map((a) => [a.id, a])),
    [accounts],
  )
  const categoriesById = useMemo(
    () => new Map((categories ?? []).map((c) => [c.id, c])),
    [categories],
  )

  const createMutation = useMutation({
    mutationFn: (values: TransactionFormValues) =>
      transactionsApi.createTransaction(formValuesToInput(values)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      setIsCreating(false)
    },
  })

  const accountsList = accounts ?? []
  const categoriesList = categories ?? []
  const canCreate = accountsList.length > 0

  return (
    <main className="mx-auto flex min-h-svh max-w-3xl flex-col gap-6 p-4 py-10">
      <PageHeader title="Transações" />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Nova transação</CardTitle>
        </CardHeader>
        <CardContent>
          {!canCreate ? (
            <p className="text-sm text-ink-muted">
              Cria pelo menos uma conta antes de registar transações.
            </p>
          ) : isCreating ? (
            <TransactionForm
              accounts={accountsList}
              categories={categoriesList}
              hasHousehold={hasHousehold}
              defaultValues={EMPTY_VALUES}
              submitLabel="Criar transação"
              onCancel={() => setIsCreating(false)}
              onSubmit={(values) => createMutation.mutateAsync(values).then(() => undefined)}
            />
          ) : (
            <Button onClick={() => setIsCreating(true)}>Adicionar transação</Button>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filtros</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="filter-account">Conta</Label>
            <Select
              id="filter-account"
              value={filters.account_id ?? ''}
              onChange={(e) =>
                setFilters((f) => ({ ...f, account_id: e.target.value || undefined }))
              }
            >
              <option value="">Todas</option>
              {accountsList.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="filter-category">Categoria</Label>
            <Select
              id="filter-category"
              value={filters.category_id ?? ''}
              onChange={(e) =>
                setFilters((f) => ({ ...f, category_id: e.target.value || undefined }))
              }
            >
              <option value="">Todas</option>
              {categoriesList.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="filter-type">Tipo</Label>
            <Select
              id="filter-type"
              value={filters.type ?? ''}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  type: (e.target.value || undefined) as TransactionFilters['type'],
                }))
              }
            >
              <option value="">Todos</option>
              {TRANSACTION_TYPES.map((t) => (
                <option key={t} value={t}>
                  {TRANSACTION_TYPE_LABELS[t]}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="filter-date-from">De</Label>
            <Input
              id="filter-date-from"
              type="date"
              value={filters.date_from ?? ''}
              onChange={(e) => setFilters((f) => ({ ...f, date_from: e.target.value || undefined }))}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="filter-date-to">Até</Label>
            <Input
              id="filter-date-to"
              type="date"
              value={filters.date_to ?? ''}
              onChange={(e) => setFilters((f) => ({ ...f, date_to: e.target.value || undefined }))}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        {isLoading && <p className="p-6 text-sm text-ink-muted">A carregar...</p>}
        {isError && (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar as transações.</p>
        )}
        {transactions && transactions.length === 0 && (
          <p className="p-6 text-sm text-ink-muted">
            Nenhuma transação encontrada.
          </p>
        )}
        {transactions?.map((transaction, index) => (
          <TransactionRow
            key={transaction.id}
            transaction={transaction}
            hasHousehold={hasHousehold}
            accounts={accountsList}
            categories={categoriesList}
            accountsById={accountsById}
            categoriesById={categoriesById}
            currency={currency}
            index={index}
          />
        ))}
      </Card>
    </main>
  )
}
