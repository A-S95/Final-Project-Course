import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ApiError } from '@/api/client'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import * as accountsApi from '@/features/accounts/api'
import { CardStatus } from '@/features/accounts/card-status'
import { ACCOUNT_TYPE_ICONS } from '@/features/accounts/icons'
import { accountSchema, type AccountFormValues } from '@/features/accounts/schemas'
import {
  ACCOUNT_TYPE_LABELS,
  ACCOUNT_TYPES,
  type Account,
  type AccountInput,
  type AccountType,
} from '@/features/accounts/types'
import { useAuth } from '@/features/auth/use-auth'

function formatMoney(value: string, currency: string) {
  return new Intl.NumberFormat('pt-PT', { style: 'currency', currency }).format(Number(value))
}

// Form usa '' para "não definido" (sem null nativo em inputs); API usa null.
function toAccountInput(values: AccountFormValues): AccountInput {
  return {
    name: values.name,
    type: values.type,
    initial_balance: values.initial_balance,
    card_expiration_date: values.card_expiration_date === '' ? null : values.card_expiration_date,
    card_plafond: values.card_plafond === '' ? null : values.card_plafond,
  }
}

// Plafond só faz sentido para cartões pré-pagos; contas normais só têm validade.
function showsExpirationField(type: AccountType) {
  return type === 'BANK' || type === 'CREDIT_CARD'
}
function showsPlafondField(type: AccountType) {
  return type === 'CREDIT_CARD'
}

function AccountForm({
  defaultValues,
  onSubmit,
  onCancel,
  submitLabel,
}: {
  defaultValues: AccountFormValues
  onSubmit: (values: AccountFormValues) => Promise<void>
  onCancel?: () => void
  submitLabel: string
}) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<AccountFormValues>({ resolver: zodResolver(accountSchema), defaultValues })
  const type = watch('type')

  const submit = async (values: AccountFormValues) => {
    setFormError(null)
    try {
      await onSubmit(values)
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Não foi possível guardar a conta.')
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
      <div className="flex flex-col gap-4">
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="name">Nome</Label>
          <Input id="name" autoComplete="off" {...register('name')} />
          {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
        </div>
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="type">Tipo</Label>
          <Select id="type" {...register('type')}>
            {ACCOUNT_TYPES.map((type) => (
              <option key={type} value={type}>
                {ACCOUNT_TYPE_LABELS[type]}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="initial_balance">Saldo inicial</Label>
          <Input id="initial_balance" inputMode="decimal" {...register('initial_balance')} />
          {errors.initial_balance && (
            <p className="text-sm text-red-600">{errors.initial_balance.message}</p>
          )}
        </div>
        {showsExpirationField(type) && (
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="card_expiration_date">Validade do cartão (opcional)</Label>
            <Input
              id="card_expiration_date"
              type="date"
              {...register('card_expiration_date')}
            />
          </div>
        )}
        {showsPlafondField(type) && (
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="card_plafond">Plafond mensal (opcional)</Label>
            <Input id="card_plafond" inputMode="decimal" {...register('card_plafond')} />
            <p className="text-xs text-ink-muted">
              Valor que este cartão deve ter todos os meses (ex: pré-pago). Recebes um aviso se o
              saldo ficar abaixo.
            </p>
            {errors.card_plafond && (
              <p className="text-sm text-red-600">{errors.card_plafond.message}</p>
            )}
          </div>
        )}
      </div>
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
      {formError && <p className="text-sm text-red-600">{formError}</p>}
    </form>
  )
}

function AccountRow({
  account,
  currency,
  index,
}: {
  account: Account
  currency: string
  index: number
}) {
  const reduceMotion = useReducedMotion()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: (values: AccountFormValues) =>
      accountsApi.updateAccount(account.id, toAccountInput(values)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      setIsEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => accountsApi.deleteAccount(account.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
    onError: (err) => {
      setDeleteError(err instanceof ApiError ? err.message : 'Não foi possível eliminar a conta.')
      setConfirmingDelete(false)
    },
  })

  if (isEditing) {
    return (
      <Card className="p-5">
        <AccountForm
          defaultValues={{
            name: account.name,
            type: account.type,
            initial_balance: account.initial_balance,
            card_expiration_date: account.card_expiration_date ?? '',
            card_plafond: account.card_plafond ?? '',
          }}
          submitLabel="Guardar"
          onCancel={() => setIsEditing(false)}
          onSubmit={(values) => updateMutation.mutateAsync(values).then(() => undefined)}
        />
      </Card>
    )
  }

  const Icon = ACCOUNT_TYPE_ICONS[account.type]

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04, ease: 'easeOut' }}
      whileHover={reduceMotion ? undefined : { y: -2 }}
      className="flex flex-col gap-4 rounded-2xl border border-border bg-surface-raised p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent-strong dark:text-accent">
          <Icon className="h-5 w-5" />
        </span>
        <div className="min-w-0">
          <p className="truncate font-medium text-ink">{account.name}</p>
          <p className="text-sm text-ink-muted">{ACCOUNT_TYPE_LABELS[account.type]}</p>
        </div>
      </div>

      <p className="text-2xl font-semibold tabular-nums text-ink">
        {formatMoney(account.current_balance, currency)}
      </p>

      <CardStatus account={account} currency={currency} formatMoney={formatMoney} />

      {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}

      <div className="flex items-center gap-2 border-t border-border pt-3">
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
    </motion.div>
  )
}

export function AccountsPage() {
  const { user } = useAuth()
  const currency = user?.currency ?? 'EUR'
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)

  const { data: accounts, isLoading, isError } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountsApi.listAccounts,
  })

  const createMutation = useMutation({
    mutationFn: (values: AccountFormValues) => accountsApi.createAccount(toAccountInput(values)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      setIsCreating(false)
    },
  })

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-[2200px] flex-col gap-6 p-4 py-10 xl:p-10">
      <PageHeader title="Contas" />

      <div className="flex flex-col gap-6 lg:flex-row-reverse lg:items-start lg:gap-8">
        <div className="w-full shrink-0 lg:sticky lg:top-10 lg:w-80">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Nova conta</CardTitle>
            </CardHeader>
            <CardContent>
              {isCreating ? (
                <AccountForm
                  defaultValues={{
                    name: '',
                    type: 'BANK',
                    initial_balance: '0',
                    card_expiration_date: '',
                    card_plafond: '',
                  }}
                  submitLabel="Criar conta"
                  onCancel={() => setIsCreating(false)}
                  onSubmit={(values) => createMutation.mutateAsync(values).then(() => undefined)}
                />
              ) : (
                <Button onClick={() => setIsCreating(true)}>Adicionar conta</Button>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="min-w-0 flex-1">
          {isLoading && <p className="text-sm text-ink-muted">A carregar...</p>}
          {isError && (
            <p className="text-sm text-red-600">Não foi possível carregar as contas.</p>
          )}
          {accounts && accounts.length === 0 && (
            <Card className="p-6 text-sm text-ink-muted">Ainda não tens nenhuma conta.</Card>
          )}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {accounts?.map((account, index) => (
              <AccountRow key={account.id} account={account} currency={currency} index={index} />
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
