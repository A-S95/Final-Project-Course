import { z } from 'zod'
import { AMOUNT_RE } from '@/lib/money'

export const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'Introduz a password'),
})
export type LoginFormValues = z.infer<typeof loginSchema>

export const forgotPasswordSchema = z.object({
  email: z.string().email('Email inválido'),
})
export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>

export const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, 'A password tem de ter pelo menos 8 caracteres')
      .max(72, 'A password não pode exceder 72 caracteres'),
    confirm: z.string(),
  })
  .refine((data) => data.password === data.confirm, {
    message: 'As passwords não coincidem',
    path: ['confirm'],
  })
export type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>

export const registerSchema = z.object({
  name: z.string().min(1, 'Introduz o teu nome'),
  email: z.string().email('Email inválido'),
  password: z
    .string()
    .min(8, 'A password tem de ter pelo menos 8 caracteres')
    .max(72, 'A password não pode exceder 72 caracteres'),
})
export type RegisterFormValues = z.infer<typeof registerSchema>

export const settingsSchema = z.object({
  name: z.string().min(1, 'Introduz o teu nome'),
  currency: z.string().min(3, 'Escolhe uma moeda').max(3),
  // Texto livre, como "amount": evita vírgula flutuante de <input type="number">.
  monthly_income: z
    .string()
    .refine((value) => value === '' || AMOUNT_RE.test(value), 'Valor inválido'),
})
export type SettingsFormValues = z.infer<typeof settingsSchema>
