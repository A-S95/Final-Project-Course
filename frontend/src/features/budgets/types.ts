export type Budget = {
  id: string
  category_id: string
  category_name: string
  period_month: string
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  amount: string
  spent: string
  remaining: string
  // Rácio para exibição (não é dinheiro) — pode passar de 100.
  percentage: number
}

export type BudgetInput = {
  category_id: string
  period_month: string
  amount: string
}
