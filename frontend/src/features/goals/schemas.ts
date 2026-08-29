import { z } from 'zod'

const decimalString = z
  .string()
  .regex(/^\d+(\.\d{1,2})?$/, 'Usa um valor com no máximo 2 casas decimais')

export const goalSchema = z.object({
  name: z.string().min(1, 'Introduz um nome'),
  target_amount: decimalString.min(1, 'Introduz um valor'),
  current_amount: z.union([decimalString, z.literal('')]),
  deadline: z.string(), // "" (sem prazo) ou "YYYY-MM-DD"
})

export type GoalFormValues = z.infer<typeof goalSchema>
