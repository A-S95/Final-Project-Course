import { apiClient } from '@/api/client'
import type { GenerateResult, RecurringExpense, RecurringExpenseInput } from './types'

const BASE_URL = '/api/v1/recurring-expenses'

export function listRecurring() {
  return apiClient.get<RecurringExpense[]>(BASE_URL)
}

export function createRecurring(payload: RecurringExpenseInput) {
  return apiClient.post<RecurringExpense>(BASE_URL, payload)
}

export function updateRecurring(id: string, payload: Partial<RecurringExpenseInput>) {
  return apiClient.patch<RecurringExpense>(`${BASE_URL}/${id}`, payload)
}

export function deleteRecurring(id: string) {
  return apiClient.delete<void>(`${BASE_URL}/${id}`)
}

export function generateRecurring() {
  return apiClient.post<GenerateResult>(`${BASE_URL}/generate`)
}
