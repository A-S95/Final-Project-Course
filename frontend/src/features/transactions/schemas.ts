import { z } from 'zod'
import { TRANSACTION_TYPES } from './types'

const decimalString = z
  .string()
  .min(1, 'Introduz um valor')
  .regex(/^\d+(\.\d{1,2})?$/, 'Usa um valor positivo com no máximo 2 casas decimais')

export const transactionSchema = z
  .object({
    account_id: z.string().min(1, 'Escolhe uma conta'),
    destination_account_id: z.string(),
    category_id: z.string(),
    type: z.enum(TRANSACTION_TYPES),
    amount: decimalString,
    description: z.string(),
    date: z.string().min(1, 'Escolhe uma data'),
    is_shared: z.boolean(),
  })
  .superRefine((values, ctx) => {
    if (values.type === 'TRANSFER') {
      if (!values.destination_account_id) {
        ctx.addIssue({
          code: 'custom',
          path: ['destination_account_id'],
          message: 'Escolhe a conta de destino',
        })
      } else if (values.destination_account_id === values.account_id) {
        ctx.addIssue({
          code: 'custom',
          path: ['destination_account_id'],
          message: 'Tem de ser diferente da conta de origem',
        })
      }
    } else if (!values.category_id) {
      ctx.addIssue({ code: 'custom', path: ['category_id'], message: 'Escolhe uma categoria' })
    }
  })

export type TransactionFormValues = z.infer<typeof transactionSchema>
