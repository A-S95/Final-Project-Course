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
import { accountSchema, type AccountFormValues } from '@/features/accounts/schemas'
import { ACCOUNT_TYPE_LABELS, ACCOUNT_TYPES, type Account } from '@/features/accounts/types'
import { useAuth } from '@/features/auth/use-auth'

function formatMoney(value: string, currency: string) {
  return new Intl.NumberFormat('pt-PT', { style: 'currency', currency }).format(Number(value))
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
    formState: { errors, isSubmitting },
  } = useForm<AccountFormValues>({ resolver: zodResolver(accountSchema), defaultValues })

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
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
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
    mutationFn: (values: AccountFormValues) => accountsApi.updateAccount(account.id, values),
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
      <div className="border-b border-border p-4 last:border-0">
        <AccountForm
          defaultValues={{
            name: account.name,
            type: account.type,
            initial_balance: account.initial_balance,
          }}
          submitLabel="Guardar"
          onCancel={() => setIsEditing(false)}
          onSubmit={(values) => updateMutation.mutateAsync(values).then(() => undefined)}
        />
      </div>
    )
  }

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04, ease: 'easeOut' }}
      className="flex flex-wrap items-center justify-between gap-3 border-b border-border p-4 last:border-0"
    >
      <div>
        <p className="font-medium text-ink">{account.name}</p>
        <p className="text-sm text-ink-muted">
          {ACCOUNT_TYPE_LABELS[account.type]}
        </p>
        {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}
      </div>
      <div className="flex items-center gap-4">
        <p className="text-lg font-semibold tabular-nums text-ink">
          {formatMoney(account.current_balance, currency)}
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
    mutationFn: accountsApi.createAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
      setIsCreating(false)
    },
  })

  return (
    <main className="mx-auto flex min-h-svh max-w-2xl flex-col gap-6 p-4 py-10">
      <PageHeader title="Contas" />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Nova conta</CardTitle>
        </CardHeader>
        <CardContent>
          {isCreating ? (
            <AccountForm
              defaultValues={{ name: '', type: 'BANK', initial_balance: '0' }}
              submitLabel="Criar conta"
              onCancel={() => setIsCreating(false)}
              onSubmit={(values) => createMutation.mutateAsync(values).then(() => undefined)}
            />
          ) : (
            <Button onClick={() => setIsCreating(true)}>Adicionar conta</Button>
          )}
        </CardContent>
      </Card>

      <Card>
        {isLoading && <p className="p-6 text-sm text-ink-muted">A carregar...</p>}
        {isError && (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar as contas.</p>
        )}
        {accounts && accounts.length === 0 && (
          <p className="p-6 text-sm text-ink-muted">
            Ainda não tens nenhuma conta.
          </p>
        )}
        {accounts?.map((account, index) => (
          <AccountRow key={account.id} account={account} currency={currency} index={index} />
        ))}
      </Card>
    </main>
  )
}
