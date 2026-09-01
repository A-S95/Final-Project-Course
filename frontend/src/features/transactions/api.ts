import { apiClient } from '@/api/client'
import type { Transaction, TransactionFilters, TransactionInput } from './types'

const BASE_URL = '/api/v1/transactions'

function filtersToQuery(filters: TransactionFilters): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value)
  }
  return params.toString()
}

export function listTransactions(filters: TransactionFilters = {}) {
  const query = filtersToQuery(filters)
  return apiClient.get<Transaction[]>(query ? `${BASE_URL}?${query}` : BASE_URL)
}

// CSV com os mesmos filtros da lista — "exporta o que estás a ver".
export function exportTransactionsCsv(filters: TransactionFilters = {}) {
  const query = filtersToQuery(filters)
  return apiClient.fetchBlob(query ? `${BASE_URL}/export?${query}` : `${BASE_URL}/export`)
}

// `allowDuplicate`: reenvia depois de o utilizador confirmar um aviso de despesa
// partilhada já lançada por outro membro do agregado (backend responde 409 sem isto).
export function createTransaction(payload: TransactionInput, allowDuplicate = false) {
  const suffix = allowDuplicate ? '?allow_duplicate=true' : ''
  return apiClient.post<Transaction>(`${BASE_URL}${suffix}`, payload)
}

export function updateTransaction(id: string, payload: TransactionInput, allowDuplicate = false) {
  const suffix = allowDuplicate ? '?allow_duplicate=true' : ''
  return apiClient.patch<Transaction>(`${BASE_URL}/${id}${suffix}`, payload)
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
