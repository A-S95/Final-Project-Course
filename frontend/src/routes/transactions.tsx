import { zodResolver } from '@hookform/resolvers/zod'
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeftRight, ChevronDown, Download, FileText, Paperclip, X } from 'lucide-react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { useLocation } from 'react-router-dom'
import { ApiError, errorMessage } from '@/api/client'
import { PageHeader } from '@/components/page-header'
import { QueryError } from '@/components/query-error'
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
import {
  addMonths,
  dayGroupLabel,
  endOfMonth,
  monthLabel,
  parseIsoDate,
  startOfMonth,
  toIsoDate,
} from '@/lib/month'
import { formatMoney } from '@/lib/money'
import { transactionSchema, type TransactionFormValues } from '@/features/transactions/schemas'
import {
  TRANSACTION_TYPE_LABELS,
  TRANSACTION_TYPES,
  type Transaction,
  type TransactionFilters,
} from '@/features/transactions/types'
import type { TransactionsLocationState } from './transactions-location-state'

const RECEIPT_ACCEPT = 'image/jpeg,image/png,image/webp,application/pdf'

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
  onSubmit: (values: TransactionFormValues) => Promise<Transaction>
  onCancel?: () => void
  submitLabel: string
}) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)
  const [receiptFile, setReceiptFile] = useState<File | null>(null)
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
      const saved = await onSubmit(values)
      if (receiptFile) {
        await transactionsApi.uploadReceipt(saved.id, receiptFile)
        queryClient.invalidateQueries({ queryKey: ['transactions'] })
      }
    } catch (err) {
      setFormError(errorMessage(err, 'Não foi possível guardar a transação.'))
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
      <div className="flex flex-col gap-4">
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

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="receipt">Recibo (opcional)</Label>
          <input
            id="receipt"
            type="file"
            accept={RECEIPT_ACCEPT}
            onChange={(e) => setReceiptFile(e.target.files?.[0] ?? null)}
            className="text-sm text-ink-muted file:mr-3 file:rounded-lg file:border file:border-border file:bg-surface-raised file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-ink hover:file:bg-surface-hover"
          />
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

// Sem categoria (transferência) usa um ícone genérico em vez do emoji.
function CategoryBadge({ category, type }: { category: Category | null; type: Transaction['type'] }) {
  if (type === 'TRANSFER' || !category) {
    return (
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent-soft text-accent-strong dark:text-accent">
        <ArrowLeftRight className="h-4 w-4" />
      </span>
    )
  }

  return (
    <span
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-base"
      style={{ backgroundColor: category.color ? `${category.color}26` : 'var(--accent-soft)' }}
    >
      {category.icon ?? '💳'}
    </span>
  )
}

function formatTime(iso: string) {
  return new Intl.DateTimeFormat('pt-PT', { hour: '2-digit', minute: '2-digit' }).format(
    new Date(iso),
  )
}

function TransactionRow({
  transaction,
  accountsById,
  categoriesById,
  currency,
  selected,
  onSelect,
  index,
}: {
  transaction: Transaction
  accountsById: Map<string, Account>
  categoriesById: Map<string, Category>
  currency: string
  selected: boolean
  onSelect: () => void
  index: number
}) {
  const reduceMotion = useReducedMotion()

  const account = accountsById.get(transaction.account_id)
  const destination = transaction.destination_account_id
    ? accountsById.get(transaction.destination_account_id)
    : null
  const category = transaction.category_id ? (categoriesById.get(transaction.category_id) ?? null) : null

  const sign = transaction.type === 'EXPENSE' ? '-' : transaction.type === 'INCOME' ? '+' : ''
  const amountColor =
    transaction.type === 'EXPENSE'
      ? 'text-red-500'
      : transaction.type === 'INCOME'
        ? 'text-emerald-500'
        : 'text-ink-muted'

  return (
    <motion.button
      type="button"
      onClick={onSelect}
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.02, ease: 'easeOut' }}
      className={`flex w-full items-center gap-3 border-b border-border p-4 text-left transition-colors last:border-0 hover:bg-surface-hover ${selected ? 'bg-accent-soft/60' : ''}`}
    >
      <CategoryBadge category={category} type={transaction.type} />
      <div className="min-w-0 flex-1">
        <p className="flex items-center gap-2 font-medium text-ink">
          <span className="truncate">
            {transaction.description || TRANSACTION_TYPE_LABELS[transaction.type]}
          </span>
          {transaction.is_shared && (
            <span className="shrink-0 rounded-full bg-accent-soft px-2 py-0.5 text-xs font-normal text-accent-strong dark:text-accent">
              Partilhada
            </span>
          )}
        </p>
        <p className="truncate text-sm text-ink-muted">
          {transaction.type === 'TRANSFER'
            ? `${account?.name ?? '?'} → ${destination?.name ?? '?'}`
            : `${category?.name ?? '?'} · ${account?.name ?? '?'}`}
        </p>
      </div>
      <div className="shrink-0 text-right">
        <p className={`text-base font-semibold tabular-nums ${amountColor}`}>
          {sign}
          {formatMoney(transaction.amount, currency)}
        </p>
        <p className="text-xs text-ink-muted">
          {dayGroupLabel(transaction.date)}, {formatTime(transaction.created_at)}
        </p>
      </div>
    </motion.button>
  )
}

function formatFullDate(iso: string) {
  return new Intl.DateTimeFormat('pt-PT', { day: 'numeric', month: 'long', year: 'numeric' }).format(
    parseIsoDate(iso),
  )
}

function ReceiptSection({ transaction }: { transaction: Transaction }) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [objectUrl, setObjectUrl] = useState<string | null>(null)
  const hasReceipt = transaction.receipt_content_type !== null

  const { data: blob } = useQuery({
    queryKey: ['receipt', transaction.id],
    queryFn: () => transactionsApi.getReceiptBlob(transaction.id),
    enabled: hasReceipt,
  })

  // Recibo protegido (sem <img src> direto, ver api/client.ts): busca-se como blob.
  useEffect(() => {
    if (!blob) {
      setObjectUrl(null)
      return
    }
    const url = URL.createObjectURL(blob)
    setObjectUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [blob])

  const uploadMutation = useMutation({
    mutationFn: (file: File) => transactionsApi.uploadReceipt(transaction.id, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['receipt', transaction.id] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => transactionsApi.deleteReceipt(transaction.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.removeQueries({ queryKey: ['receipt', transaction.id] })
    },
  })

  const isImage = transaction.receipt_content_type?.startsWith('image/')

  return (
    <div className="flex flex-col gap-2 border-t border-border pt-4">
      <p className="text-sm font-medium text-ink">Recibo</p>
      {!hasReceipt ? (
        <>
          <input
            ref={fileInputRef}
            type="file"
            accept={RECEIPT_ACCEPT}
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) uploadMutation.mutate(file)
              e.target.value = ''
            }}
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={uploadMutation.isPending}
            onClick={() => fileInputRef.current?.click()}
          >
            <Paperclip className="mr-1.5 h-4 w-4" />
            {uploadMutation.isPending ? 'A enviar...' : 'Anexar recibo'}
          </Button>
          {uploadMutation.isError && (
            <p className="text-sm text-red-600">
              {uploadMutation.error instanceof ApiError
                ? uploadMutation.error.message
                : 'Não foi possível anexar o recibo.'}
            </p>
          )}
        </>
      ) : (
        <div className="flex flex-col gap-2">
          {isImage && objectUrl ? (
            <a href={objectUrl} target="_blank" rel="noreferrer">
              <img
                src={objectUrl}
                alt="Recibo"
                className="max-h-48 w-full rounded-lg border border-border object-contain"
              />
            </a>
          ) : (
            <a
              href={objectUrl ?? undefined}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 rounded-lg border border-border p-3 text-sm text-ink hover:bg-surface-hover"
            >
              <FileText className="h-4 w-4" /> Ver recibo (PDF)
            </a>
          )}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={deleteMutation.isPending}
            onClick={() => deleteMutation.mutate()}
          >
            Remover recibo
          </Button>
        </div>
      )}
    </div>
  )
}

function TransactionDetailPanel({
  transaction,
  accounts,
  categories,
  hasHousehold,
  accountsById,
  categoriesById,
  currency,
  onClose,
}: {
  transaction: Transaction
  accounts: Account[]
  categories: Category[]
  hasHousehold: boolean
  accountsById: Map<string, Account>
  categoriesById: Map<string, Category>
  currency: string
  onClose: () => void
}) {
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
      onClose()
    },
  })

  if (isEditing) {
    return (
      <Card>
        <CardHeader className="flex-row items-center justify-between">
          <CardTitle className="text-base">Editar transação</CardTitle>
          <button
            type="button"
            onClick={() => setIsEditing(false)}
            aria-label="Cancelar edição"
            className="text-ink-muted hover:text-ink"
          >
            <X className="h-4 w-4" />
          </button>
        </CardHeader>
        <CardContent>
          <TransactionForm
            accounts={accounts}
            categories={categories}
            hasHousehold={hasHousehold}
            defaultValues={transactionToFormValues(transaction)}
            submitLabel="Guardar"
            onCancel={() => setIsEditing(false)}
            onSubmit={(values) => updateMutation.mutateAsync(values)}
          />
        </CardContent>
      </Card>
    )
  }

  const account = accountsById.get(transaction.account_id)
  const destination = transaction.destination_account_id
    ? accountsById.get(transaction.destination_account_id)
    : null
  const category = transaction.category_id ? (categoriesById.get(transaction.category_id) ?? null) : null
  const sign = transaction.type === 'EXPENSE' ? '-' : transaction.type === 'INCOME' ? '+' : ''
  const amountColor =
    transaction.type === 'EXPENSE'
      ? 'text-red-500'
      : transaction.type === 'INCOME'
        ? 'text-emerald-500'
        : 'text-ink-muted'

  return (
    <Card>
      <CardContent className="flex flex-col gap-4 pt-6">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <CategoryBadge category={category} type={transaction.type} />
            <div>
              <p className="font-medium text-ink">
                {transaction.description || TRANSACTION_TYPE_LABELS[transaction.type]}
              </p>
              <p className="text-sm text-ink-muted">
                {dayGroupLabel(transaction.date)}, {formatTime(transaction.created_at)}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar"
            className="text-ink-muted hover:text-ink"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className={`text-2xl font-semibold tabular-nums ${amountColor}`}>
          {sign}
          {formatMoney(transaction.amount, currency)}
        </p>

        <div className="flex flex-col gap-2 text-sm">
          <div className="flex items-center justify-between border-t border-border pt-2">
            <span className="text-ink-muted">
              {transaction.type === 'TRANSFER' ? 'Conta de origem' : 'Conta'}
            </span>
            <span className="text-ink">{account?.name ?? '—'}</span>
          </div>
          {transaction.type === 'TRANSFER' ? (
            <div className="flex items-center justify-between">
              <span className="text-ink-muted">Conta de destino</span>
              <span className="text-ink">{destination?.name ?? '—'}</span>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <span className="text-ink-muted">Categoria</span>
              <span className="text-ink">{category?.name ?? '—'}</span>
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="text-ink-muted">Data</span>
            <span className="text-ink">{formatFullDate(transaction.date)}</span>
          </div>
          {transaction.is_shared && (
            <div className="flex items-center justify-between">
              <span className="text-ink-muted">Partilhada</span>
              <span className="text-ink">Sim</span>
            </div>
          )}
        </div>

        <ReceiptSection transaction={transaction} />

        {confirmingDelete ? (
          <div className="flex items-center gap-2 border-t border-border pt-4">
            <span className="text-sm text-ink-muted">Eliminar esta transação?</span>
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
          <div className="flex gap-2 border-t border-border pt-4">
            <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
              Editar
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setConfirmingDelete(true)}>
              Eliminar
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Modal, não painel encaixado: um painel no fluxo normal da página aparecia
// fora do scroll atual quando a lista já ia longa.
function TransactionDetailModal({
  transaction,
  accounts,
  categories,
  hasHousehold,
  accountsById,
  categoriesById,
  currency,
  onClose,
}: {
  transaction: Transaction | null
  accounts: Account[]
  categories: Category[]
  hasHousehold: boolean
  accountsById: Map<string, Account>
  categoriesById: Map<string, Category>
  currency: string
  onClose: () => void
}) {
  const reduceMotion = useReducedMotion()

  return (
    <AnimatePresence>
      {transaction && (
        <motion.div
          key="backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          onClick={(e) => {
            if (e.target === e.currentTarget) onClose()
          }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
        >
          <motion.div
            initial={reduceMotion ? { opacity: 0 } : { opacity: 0, scale: 0.96, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={reduceMotion ? { opacity: 0 } : { opacity: 0, scale: 0.96, y: 12 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="max-h-[85vh] w-full max-w-md overflow-y-auto"
          >
            <TransactionDetailPanel
              transaction={transaction}
              accounts={accounts}
              categories={categories}
              hasHousehold={hasHousehold}
              accountsById={accountsById}
              categoriesById={categoriesById}
              currency={currency}
              onClose={onClose}
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export function TransactionsPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const queryClient = useQueryClient()
  const reduceMotion = useReducedMotion()
  const location = useLocation()

  // state.prefillTransaction (botão "Recarregar plafond") abre o form já preenchido.
  // Limpa via history.replaceState, não navigate(): isso chegou a repor o componente.
  const [prefillValues] = useState<Partial<TransactionFormValues> | null>(
    () => (location.state as TransactionsLocationState | null)?.prefillTransaction ?? null,
  )
  useEffect(() => {
    if (prefillValues) {
      window.history.replaceState(
        { ...window.history.state, usr: null },
        '',
        window.location.href,
      )
    }
  }, [prefillValues])

  const [isCreating, setIsCreating] = useState(() => Boolean(prefillValues))
  // Painel da direita mostra só uma coisa de cada vez: criação OU detalhe.
  const [selectedId, setSelectedId] = useState<string | null>(null)
  // Fechados por omissão em ecrãs pequenos, abertos em desktop; não segue resize.
  const [filtersOpen, setFiltersOpen] = useState(() => window.matchMedia('(min-width: 1024px)').matches)

  // Só o mês atual por omissão — uma conta com um ano de histórico chegou a
  // renderizar páginas de 16 000px de uma vez. "Ver todas" dá acesso ao resto.
  const thisMonth = useMemo(() => startOfMonth(new Date()), [])
  const [monthCursor, setMonthCursor] = useState(thisMonth)
  const [showingAll, setShowingAll] = useState(false)
  const [filters, setFilters] = useState<TransactionFilters>({
    date_from: toIsoDate(thisMonth),
    date_to: toIsoDate(endOfMonth(thisMonth)),
  })

  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState(false)

  const goToMonth = (next: Date) => {
    setMonthCursor(next)
    setShowingAll(false)
    setFilters((f) => ({ ...f, date_from: toIsoDate(next), date_to: toIsoDate(endOfMonth(next)) }))
  }

  const handleExport = async () => {
    setExporting(true)
    setExportError(false)
    try {
      // Um <img>/<a> normal não leva o header Authorization — busca-se como blob
      // autenticado e força-se o download com um <a download> temporário.
      const blob = await transactionsApi.exportTransactionsCsv(filters)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `centisible-transacoes-${toIsoDate(new Date())}.csv`
      document.body.append(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch {
      setExportError(true)
    } finally {
      setExporting(false)
    }
  }

  const toggleShowAll = () => {
    if (showingAll) {
      goToMonth(thisMonth)
      return
    }
    setShowingAll(true)
    setFilters((f) => ({ ...f, date_from: undefined, date_to: undefined }))
  }

  const { data: accounts, isError: accountsError } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountsApi.listAccounts,
  })
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.listCategories,
  })
  const { data: household } = useQuery({ queryKey: ['household'], queryFn: getMyHousehold })
  const hasHousehold = Boolean(household)
  const {
    data: transactions,
    isLoading,
    isFetching,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => transactionsApi.listTransactions(filters),
    placeholderData: keepPreviousData,
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
  // Procurado a cada render, não guardado à parte, para o painel aberto
  // refletir sozinho qualquer mutação que invalide ['transactions'].
  const selectedTransaction = transactions?.find((t) => t.id === selectedId) ?? null

  // API já devolve por data decrescente — só junta consecutivos do mesmo dia.
  const transactionGroups = useMemo(() => {
    const groups: { date: string; items: Transaction[] }[] = []
    for (const transaction of transactions ?? []) {
      const last = groups[groups.length - 1]
      if (last && last.date === transaction.date) {
        last.items.push(transaction)
      } else {
        groups.push({ date: transaction.date, items: [transaction] })
      }
    }
    return groups
  }, [transactions])
  // Só os filtros opcionais contam (o intervalo de datas está sempre definido).
  const activeFilterCount = [filters.account_id, filters.category_id, filters.type].filter(
    Boolean,
  ).length

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-[2200px] flex-col gap-6 p-4 py-10 xl:p-10">
      <PageHeader title="Transações" />

      <TransactionDetailModal
        transaction={selectedTransaction}
        accounts={accountsList}
        categories={categoriesList}
        hasHousehold={hasHousehold}
        accountsById={accountsById}
        categoriesById={categoriesById}
        currency={currency}
        onClose={() => setSelectedId(null)}
      />

      <div className="flex flex-col gap-6 lg:flex-row-reverse lg:items-start lg:gap-8">
        <div className="w-full shrink-0 lg:sticky lg:top-10 lg:w-80">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Nova transação</CardTitle>
            </CardHeader>
            <CardContent>
              {accountsError ? (
                <p className="text-sm text-red-600">
                  Não foi possível carregar as contas. Atualiza a página e tenta de novo.
                </p>
              ) : !canCreate ? (
                <p className="text-sm text-ink-muted">
                  Cria pelo menos uma conta antes de registar transações.
                </p>
              ) : isCreating ? (
                <TransactionForm
                  accounts={accountsList}
                  categories={categoriesList}
                  hasHousehold={hasHousehold}
                  defaultValues={{ ...EMPTY_VALUES, ...prefillValues }}
                  submitLabel="Criar transação"
                  onCancel={() => setIsCreating(false)}
                  onSubmit={(values) => createMutation.mutateAsync(values)}
                />
              ) : (
                <Button onClick={() => setIsCreating(true)}>Adicionar transação</Button>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="flex min-w-0 flex-1 flex-col gap-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={showingAll}
                onClick={() => goToMonth(addMonths(monthCursor, -1))}
              >
                ‹
              </Button>
              <span className="min-w-36 text-center text-sm font-medium text-ink">
                {showingAll ? 'Todo o histórico' : monthLabel(monthCursor)}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={showingAll}
                onClick={() => goToMonth(addMonths(monthCursor, 1))}
              >
                ›
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={toggleShowAll}>
                {showingAll ? 'Ver só este mês' : 'Ver todas as transações'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={exporting || !transactions?.length}
                onClick={handleExport}
              >
                <Download className="mr-1.5 h-4 w-4" />
                {exporting ? 'A exportar...' : 'Exportar CSV'}
              </Button>
            </div>
          </div>
          {exportError && (
            <p className="text-sm text-red-600">Não foi possível exportar. Tenta novamente.</p>
          )}

          <Card>
            <button
              type="button"
              onClick={() => setFiltersOpen((open) => !open)}
              aria-expanded={filtersOpen}
              className="flex w-full items-center justify-between gap-3 p-6 text-left"
            >
              <span className="flex items-center gap-2">
                <CardTitle className="text-base">Filtros</CardTitle>
                {activeFilterCount > 0 && (
                  <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent-strong dark:text-accent">
                    {activeFilterCount}
                  </span>
                )}
              </span>
              <ChevronDown
                className={`h-4 w-4 shrink-0 text-ink-muted transition-transform ${filtersOpen ? 'rotate-180' : ''}`}
              />
            </button>
            <AnimatePresence initial={false}>
              {filtersOpen && (
                <motion.div
                  initial={reduceMotion ? false : { height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={reduceMotion ? undefined : { height: 0, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeOut' }}
                  className="overflow-hidden"
                >
                  <CardContent className="grid grid-cols-1 gap-4 pt-0 sm:grid-cols-2 lg:grid-cols-4">
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
                        onChange={(e) =>
                          setFilters((f) => ({ ...f, date_from: e.target.value || undefined }))
                        }
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label htmlFor="filter-date-to">Até</Label>
                      <Input
                        id="filter-date-to"
                        type="date"
                        value={filters.date_to ?? ''}
                        onChange={(e) =>
                          setFilters((f) => ({ ...f, date_to: e.target.value || undefined }))
                        }
                      />
                    </div>
                  </CardContent>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          <Card
            className={`transition-opacity duration-300 ${isFetching ? 'opacity-60' : 'opacity-100'}`}
          >
            {isLoading && <p className="p-6 text-sm text-ink-muted">A carregar...</p>}
            {isError && (
              <div className="p-6">
                <QueryError
                  message="Não foi possível carregar as transações."
                  onRetry={() => refetch()}
                />
              </div>
            )}
            {transactions && transactions.length === 0 && (
              <p className="p-6 text-sm text-ink-muted">
                Nenhuma transação encontrada.
              </p>
            )}
            {transactionGroups.map((group) => (
              <div key={group.date}>
                <p className="border-b border-border bg-surface-hover px-4 py-2 text-xs font-medium uppercase tracking-wide text-ink-muted">
                  {dayGroupLabel(group.date)}
                </p>
                {group.items.map((transaction, index) => (
                  <TransactionRow
                    key={transaction.id}
                    transaction={transaction}
                    accountsById={accountsById}
                    categoriesById={categoriesById}
                    currency={currency}
                    selected={transaction.id === selectedId}
                    onSelect={() => {
                      setSelectedId(transaction.id)
                      setIsCreating(false)
                    }}
                    index={index}
                  />
                ))}
              </div>
            ))}
          </Card>
        </div>
      </div>
    </main>
  )
}
