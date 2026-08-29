import { apiClient } from '@/api/client'
import type { DashboardScope, DashboardSummary } from './types'

const BASE_URL = '/api/v1/dashboard'

/** `month` é qualquer dia do mês pretendido, no formato "YYYY-MM-DD". */
export function getDashboard(month: string, scope: DashboardScope = 'individual') {
  return apiClient.get<DashboardSummary>(`${BASE_URL}?month=${month}&scope=${scope}`)
}
