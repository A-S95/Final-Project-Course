import { apiClient } from '@/api/client'
import type { AuthResponse, User } from './types'

export function registerUser(payload: { email: string; password: string; name: string }) {
  return apiClient.post<AuthResponse>('/api/v1/auth/register', payload, { skipAuthRetry: true })
}

export function updateMe(payload: {
  name: string
  currency: string
  monthly_income: string | null
}) {
  return apiClient.patch<User>('/api/v1/users/me', payload)
}

export function loginUser(payload: { email: string; password: string }) {
  return apiClient.post<AuthResponse>('/api/v1/auth/login', payload, { skipAuthRetry: true })
}

export function logoutUser() {
  return apiClient.post<void>('/api/v1/auth/logout', undefined, { skipAuthRetry: true })
}

export function requestPasswordReset(email: string) {
  return apiClient.post<{ detail: string }>(
    '/api/v1/auth/password-reset/request',
    { email },
    { skipAuthRetry: true },
  )
}

export function confirmPasswordReset(token: string, password: string) {
  return apiClient.post<{ detail: string }>(
    '/api/v1/auth/password-reset/confirm',
    { token, password },
    { skipAuthRetry: true },
  )
}
