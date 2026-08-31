import { apiClient } from '@/api/client'
import type { Account, AccountInput } from './types'

const BASE_URL = '/api/v1/accounts'

export function listAccounts() {
  return apiClient.get<Account[]>(BASE_URL)
}

export function createAccount(payload: AccountInput) {
  return apiClient.post<Account>(BASE_URL, payload)
}

export function updateAccount(id: string, payload: AccountInput) {
  return apiClient.patch<Account>(`${BASE_URL}/${id}`, payload)
}

export function deleteAccount(id: string) {
  return apiClient.delete<void>(`${BASE_URL}/${id}`)
}
