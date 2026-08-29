export type DashboardScope = 'individual' | 'household'

export type CategoryExpense = {
  category_id: string
  name: string
  color: string | null
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  total: string
}

export type DashboardSummary = {
  // Primeiro dia do mês do resumo (ex: "2026-08-01").
  month: string
  // Vista efetivamente devolvida (se pediste "household" sem agregado, vem "individual").
  scope: DashboardScope
  total_balance: string
  total_income: string
  total_expenses: string
  net: string
  // Rácio para exibição (não é dinheiro) — número ou null se não houve receitas.
  savings_rate: number | null
  expenses_by_category: CategoryExpense[]
  // Quanto de `total_expenses` foi marcado como despesa partilhada do
  // agregado — só relevante quando `scope === 'household'`.
  shared_expenses_total: string
}
