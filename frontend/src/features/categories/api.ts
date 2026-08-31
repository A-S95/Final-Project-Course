import { apiClient } from '@/api/client'
import type { Category, CategoryInput } from './types'

const BASE_URL = '/api/v1/categories'

export function listCategories() {
  return apiClient.get<Category[]>(BASE_URL)
}

export function createCategory(payload: CategoryInput) {
  return apiClient.post<Category>(BASE_URL, payload)
}

export function updateCategory(id: string, payload: CategoryInput) {
  return apiClient.patch<Category>(`${BASE_URL}/${id}`, payload)
}

export function deleteCategory(id: string, reassignToCategoryId?: string) {
  const query = reassignToCategoryId
    ? `?reassign_to_category_id=${encodeURIComponent(reassignToCategoryId)}`
    : ''
  return apiClient.delete<void>(`${BASE_URL}/${id}${query}`)
}
