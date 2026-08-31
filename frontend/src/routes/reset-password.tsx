import { zodResolver } from '@hookform/resolvers/zod'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useSearchParams } from 'react-router-dom'
import { ApiError } from '@/api/client'
import { LogoMark } from '@/components/logo'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button, buttonVariants } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import * as authApi from '@/features/auth/api'
import { resetPasswordSchema, type ResetPasswordFormValues } from '@/features/auth/schemas'

export function ResetPasswordPage() {
  const reduceMotion = useReducedMotion()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [done, setDone] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormValues>({ resolver: zodResolver(resetPasswordSchema) })

  const onSubmit = async (values: ResetPasswordFormValues) => {
    setFormError(null)
    try {
      await authApi.confirmPasswordReset(token, values.password)
      setDone(true)
    } catch (err) {
      setFormError(
        err instanceof ApiError
          ? err.message
          : 'Não foi possível alterar a password. Tenta de novo.',
      )
    }
  }

  return (
    <main className="relative flex min-h-svh items-center justify-center bg-canvas p-4">
      <ThemeToggle className="absolute right-4 top-4" />
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-full max-w-sm"
      >
        <Link
          to="/"
          className="font-display mb-6 flex items-center justify-center gap-2 text-lg font-semibold text-ink"
        >
          <LogoMark className="h-7 w-7" />
          CentiSible
        </Link>
        <Card>
          <CardHeader>
            <CardTitle>Nova password</CardTitle>
            <CardDescription>
              {done
                ? 'Está feito.'
                : 'Escolhe uma password nova. Depois de a guardar, todas as sessões abertas terminam.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {done ? (
              <div className="flex flex-col gap-4">
                <p className="text-sm text-ink">
                  A tua password foi alterada. Já podes iniciar sessão com a nova.
                </p>
                <Link to="/login" className={buttonVariants()}>
                  Iniciar sessão
                </Link>
              </div>
            ) : !token ? (
              <div className="flex flex-col gap-4">
                <p className="text-sm text-red-600">
                  Ligação inválida — falta o código de recuperação. Pede uma nova.
                </p>
                <Link
                  to="/recuperar-password"
                  className={buttonVariants({ variant: 'outline' })}
                >
                  Pedir nova ligação
                </Link>
              </div>
            ) : (
              <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="password">Password nova</Label>
                  <Input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    {...register('password')}
                  />
                  {errors.password && (
                    <p className="text-sm text-red-600">{errors.password.message}</p>
                  )}
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="confirm">Confirmar password</Label>
                  <Input
                    id="confirm"
                    type="password"
                    autoComplete="new-password"
                    {...register('confirm')}
                  />
                  {errors.confirm && (
                    <p className="text-sm text-red-600">{errors.confirm.message}</p>
                  )}
                </div>
                {formError && <p className="text-sm text-red-600">{formError}</p>}
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'A guardar...' : 'Guardar password'}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </main>
  )
}
