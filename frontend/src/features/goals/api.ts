import { apiClient } from '@/api/client'
import type { Goal, GoalInput } from './types'

const BASE_URL = '/api/v1/goals'

export function listGoals() {
  return apiClient.get<Goal[]>(BASE_URL)
}

export function createGoal(payload: GoalInput) {
  return apiClient.post<Goal>(BASE_URL, payload)
}

export function updateGoal(id: string, payload: GoalInput) {
  return apiClient.patch<Goal>(`${BASE_URL}/${id}`, payload)
}

export function contributeToGoal(id: string, amount: string) {
  return apiClient.post<Goal>(`${BASE_URL}/${id}/contributions`, { amount })
}

export function deleteGoal(id: string) {
  return apiClient.delete<void>(`${BASE_URL}/${id}`)
}
