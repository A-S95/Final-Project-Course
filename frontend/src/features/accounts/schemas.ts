import { z } from 'zod'
import { ACCOUNT_TYPES } from './types'

// Aceita "100", "100.50", "-20.00", nunca mais de 2 casas. Validação a sério fica no backend.
const decimalString = z
  .string()
  .min(1, 'Introduz um valor')
  .regex(/^-?\d+(\.\d{1,2})?$/, 'Usa um valor numérico com no máximo 2 casas decimais')

// Plafond: como initial_balance mas opcional; '' vira null antes de enviar ao backend.
const optionalDecimalString = z
  .string()
  .regex(/^-?\d+(\.\d{1,2})?$/, 'Usa um valor numérico com no máximo 2 casas decimais')
  .or(z.literal(''))

export const accountSchema = z.object({
  name: z.string().min(1, 'Introduz um nome'),
  type: z.enum(ACCOUNT_TYPES),
  initial_balance: decimalString,
  // Data (input type="date") ou '' — mesma convenção de "vazio = não definido".
  card_expiration_date: z.string(),
  card_plafond: optionalDecimalString,
})
export type AccountFormValues = z.infer<typeof accountSchema>
