import { z } from 'zod'
import { RECURRING_FREQUENCIES } from './types'

export const recurringSchema = z.object({
  account_id: z.string().min(1, 'Escolhe uma conta'),
  category_id: z.string().min(1, 'Escolhe uma categoria'),
  description: z.string().min(1, 'Introduz uma descrição'),
  amount: z
    .string()
    .min(1, 'Introduz um valor')
    .regex(/^\d+(\.\d{1,2})?$/, 'Usa um valor com no máximo 2 casas decimais'),
  frequency: z.enum(RECURRING_FREQUENCIES),
  next_occurrence: z.string().min(1, 'Escolhe uma data'),
  active: z.boolean(),
})

export type RecurringFormValues = z.infer<typeof recurringSchema>
