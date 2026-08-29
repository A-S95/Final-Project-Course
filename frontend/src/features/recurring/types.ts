export const RECURRING_FREQUENCIES = ['MONTHLY', 'YEARLY'] as const
export type RecurringFrequency = (typeof RECURRING_FREQUENCIES)[number]

export const FREQUENCY_LABELS: Record<RecurringFrequency, string> = {
  MONTHLY: 'Mensal',
  YEARLY: 'Anual',
}

export type RecurringExpense = {
  id: string
  account_id: string
  account_name: string
  category_id: string
  category_name: string
  description: string
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  amount: string
  frequency: RecurringFrequency
  day_of_month: number
  next_occurrence: string
  active: boolean
  // Vencida e ativa — tem transações por gerar.
  is_due: boolean
  created_at: string
  updated_at: string
}

export type RecurringExpenseInput = {
  account_id: string
  category_id: string
  description: string
  amount: string
  frequency: RecurringFrequency
  next_occurrence: string
  active: boolean
}

export type GenerateResult = {
  generated: number
}
