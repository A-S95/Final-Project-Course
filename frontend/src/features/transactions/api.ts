import { apiClient } from '@/api/client'
import type { Transaction, TransactionFilters, TransactionInput } from './types'

const BASE_URL = '/api/v1/transactions'

export function listTransactions(filters: TransactionFilters = {}) {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value)
  }
  const query = params.toString()
  return apiClient.get<Transaction[]>(query ? `${BASE_URL}?${query}` : BASE_URL)
}

export function createTransaction(payload: TransactionInput) {
  return apiClient.post<Transaction>(BASE_URL, payload)
}

export function updateTransaction(id: string, payload: TransactionInput) {
  return apiClient.patch<Transaction>(`${BASE_URL}/${id}`, payload)
}

export function deleteTransaction(id: string) {
  return apiClient.delete<void>(`${BASE_URL}/${id}`)
}

export function uploadReceipt(id: string, file: File) {
  return apiClient.uploadFile<Transaction>(`${BASE_URL}/${id}/receipt`, file)
}

export async function getReceiptBlob(id: string) {
  return apiClient.fetchBlob(`${BASE_URL}/${id}/receipt`)
}

export function deleteReceipt(id: string) {
  return apiClient.delete<Transaction>(`${BASE_URL}/${id}/receipt`)
}
