import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'Introduz a password'),
})
export type LoginFormValues = z.infer<typeof loginSchema>

export const registerSchema = z.object({
  name: z.string().min(1, 'Introduz o teu nome'),
  email: z.string().email('Email inválido'),
  password: z
    .string()
    .min(8, 'A password tem de ter pelo menos 8 caracteres')
    .max(72, 'A password não pode exceder 72 caracteres'),
})
export type RegisterFormValues = z.infer<typeof registerSchema>

const AMOUNT_RE = /^\d+(\.\d{1,2})?$/

export const settingsSchema = z.object({
  name: z.string().min(1, 'Introduz o teu nome'),
  currency: z.string().min(3, 'Escolhe uma moeda').max(3),
  // Texto livre (como o "amount" de uma transação) em vez de number — evita
  // os problemas de vírgula flutuante do <input type="number"> e mantém a
  // mesma validação usada em budgets.tsx/accounts.tsx.
  monthly_income: z
    .string()
    .refine((value) => value === '' || AMOUNT_RE.test(value), 'Valor inválido'),
})
export type SettingsFormValues = z.infer<typeof settingsSchema>
