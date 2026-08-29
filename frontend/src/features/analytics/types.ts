export type MonthTotals = {
  month: string
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  total_income: string
  total_expenses: string
  net: string
}

export type MonthComparison = {
  current: MonthTotals
  previous: MonthTotals
  income_change: string
  expenses_change: string
  net_change: string
  income_change_pct: number | null
  expenses_change_pct: number | null
}

export type MonthlyTrend = {
  points: MonthTotals[]
}
