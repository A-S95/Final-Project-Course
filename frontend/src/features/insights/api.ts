import { apiClient } from '@/api/client'
import type { Insight } from './types'

/** `month` é qualquer dia do mês pretendido, no formato "YYYY-MM-DD". */
export function getInsights(month: string) {
  return apiClient.get<Insight[]>(`/api/v1/insights?month=${month}`)
}
