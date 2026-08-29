import { apiClient } from '@/api/client'
import type { MonthComparison, MonthlyTrend } from './types'

const BASE_URL = '/api/v1/analytics'

/** `month` é qualquer dia do mês pretendido, no formato "YYYY-MM-DD". */
export function getMonthlyComparison(month: string) {
  return apiClient.get<MonthComparison>(`${BASE_URL}/monthly-comparison?month=${month}`)
}

export function getMonthlyTrend(month: string, months = 6) {
  return apiClient.get<MonthlyTrend>(
    `${BASE_URL}/monthly-trend?month=${month}&months=${months}`,
  )
}
