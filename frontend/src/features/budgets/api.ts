import { apiClient } from '@/api/client'
import type { Budget, BudgetInput } from './types'

const BASE_URL = '/api/v1/budgets'

/** `month` é qualquer dia do mês pretendido, no formato "YYYY-MM-DD". */
export function listBudgets(month: string) {
  return apiClient.get<Budget[]>(`${BASE_URL}?month=${month}`)
}

export function createBudget(payload: BudgetInput) {
  return apiClient.post<Budget>(BASE_URL, payload)
}

export function updateBudget(id: string, amount: string) {
  return apiClient.patch<Budget>(`${BASE_URL}/${id}`, { amount })
}

export function deleteBudget(id: string) {
  return apiClient.delete<void>(`${BASE_URL}/${id}`)
}
