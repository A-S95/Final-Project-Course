export type Goal = {
  id: string
  name: string
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  target_amount: string
  current_amount: string
  deadline: string | null
  remaining: string
  progress_percentage: number
  is_achieved: boolean
  deadline_passed: boolean
  months_until_deadline: number | null
  required_monthly_contribution: string | null
  created_at: string
  updated_at: string
}

export type GoalInput = {
  name: string
  target_amount: string
  current_amount: string
  deadline: string | null
}
