import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ApiError } from '@/api/client'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import * as authApi from '@/features/auth/api'
import { settingsSchema, type SettingsFormValues } from '@/features/auth/schemas'
import { CURRENCIES, CURRENCY_LABELS } from '@/features/auth/types'
import { useAuth } from '@/features/auth/use-auth'

export function SettingsPage() {
  const { user, updateUser } = useAuth()
  const [formError, setFormError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      name: user?.name ?? '',
      currency: user?.currency ?? 'EUR',
      monthly_income: user?.monthly_income ?? '',
    },
  })

  if (!user) return null

  const onSubmit = async (values: SettingsFormValues) => {
    setFormError(null)
    setSaved(false)
    try {
      const updated = await authApi.updateMe({
        name: values.name,
        currency: values.currency,
        monthly_income: values.monthly_income === '' ? null : values.monthly_income,
      })
      updateUser(updated)
      setSaved(true)
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : 'Não foi possível guardar as definições.',
      )
    }
  }

  return (
    <main className="mx-auto flex min-h-svh max-w-lg flex-col gap-6 p-4 py-10">
      <PageHeader title="Definições" />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Perfil</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4"
            onSubmit={handleSubmit(onSubmit)}
            noValidate
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={user.email} disabled />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="name">Nome</Label>
              <Input id="name" autoComplete="name" {...register('name')} />
              {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="currency">Moeda</Label>
              <Select id="currency" {...register('currency')}>
                {CURRENCIES.map((currency) => (
                  <option key={currency} value={currency}>
                    {CURRENCY_LABELS[currency]}
                  </option>
                ))}
              </Select>
              {errors.currency && (
                <p className="text-sm text-red-600">{errors.currency.message}</p>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="monthly_income">Rendimento mensal (opcional)</Label>
              <Input
                id="monthly_income"
                inputMode="decimal"
                placeholder="0.00"
                {...register('monthly_income')}
              />
              <p className="text-xs text-ink-subtle">
                Informativo — a taxa de poupança do dashboard usa sempre as
                receitas reais registadas, não este valor.
              </p>
              {errors.monthly_income && (
                <p className="text-sm text-red-600">{errors.monthly_income.message}</p>
              )}
            </div>

            {saved && <p className="text-sm text-emerald-500">Definições guardadas.</p>}
            {formError && <p className="text-sm text-red-600">{formError}</p>}

            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'A guardar...' : 'Guardar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
