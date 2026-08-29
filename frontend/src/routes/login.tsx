import { zodResolver } from '@hookform/resolvers/zod'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { ApiError } from '@/api/client'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { loginSchema, type LoginFormValues } from '@/features/auth/schemas'
import { useAuth } from '@/features/auth/use-auth'

export function LoginPage() {
  const { login, status } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [formError, setFormError] = useState<string | null>(null)
  const reduceMotion = useReducedMotion()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) })

  if (status === 'authenticated') {
    const redirectTo = (location.state as { from?: string } | null)?.from ?? '/dashboard'
    return <Navigate to={redirectTo} replace />
  }

  const onSubmit = async (values: LoginFormValues) => {
    setFormError(null)
    try {
      await login(values.email, values.password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Não foi possível iniciar sessão.')
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
          <span className="brand-gradient flex h-7 w-7 items-center justify-center rounded-lg text-sm font-bold text-white">
            F
          </span>
          FinTrack
        </Link>
        <Card>
          <CardHeader>
            <CardTitle>Entrar</CardTitle>
            <CardDescription>Introduz as tuas credenciais para continuar.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" autoComplete="email" {...register('email')} />
                {errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  {...register('password')}
                />
                {errors.password && (
                  <p className="text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>
              {formError && <p className="text-sm text-red-600">{formError}</p>}
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'A entrar...' : 'Entrar'}
              </Button>
            </form>
            <p className="mt-4 text-center text-sm text-ink-muted">
              Ainda não tens conta?{' '}
              <Link to="/registar" className="font-medium text-ink underline">
                Regista-te
              </Link>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </main>
  )
}
