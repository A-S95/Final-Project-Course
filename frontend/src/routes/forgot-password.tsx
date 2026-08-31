import { zodResolver } from '@hookform/resolvers/zod'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { ApiError } from '@/api/client'
import { LogoMark } from '@/components/logo'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button, buttonVariants } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import * as authApi from '@/features/auth/api'
import { forgotPasswordSchema, type ForgotPasswordFormValues } from '@/features/auth/schemas'

export function ForgotPasswordPage() {
  const reduceMotion = useReducedMotion()
  const [sent, setSent] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormValues>({ resolver: zodResolver(forgotPasswordSchema) })

  const onSubmit = async (values: ForgotPasswordFormValues) => {
    setFormError(null)
    try {
      await authApi.requestPasswordReset(values.email)
      setSent(true)
    } catch (err) {
      setFormError(
        err instanceof ApiError ? err.message : 'Não foi possível enviar o email. Tenta de novo.',
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
            <CardTitle>Recuperar password</CardTitle>
            <CardDescription>
              Escreve o email da tua conta e enviamos-te uma ligação para escolher uma password nova.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sent ? (
              <div className="flex flex-col gap-4">
                <p className="text-sm text-ink">
                  Se existir uma conta com esse email, vais receber uma mensagem com as instruções
                  dentro de instantes. A ligação expira dentro de 1 hora.
                </p>
                <Link to="/login" className={buttonVariants({ variant: 'outline' })}>
                  Voltar ao início de sessão
                </Link>
              </div>
            ) : (
              <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" autoComplete="email" {...register('email')} />
                  {errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}
                </div>
                {formError && <p className="text-sm text-red-600">{formError}</p>}
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'A enviar...' : 'Enviar ligação'}
                </Button>
              </form>
            )}
            <p className="mt-4 text-center text-sm text-ink-muted">
              Lembraste-te?{' '}
              <Link to="/login" className="font-medium text-ink underline">
                Iniciar sessão
              </Link>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </main>
  )
}
