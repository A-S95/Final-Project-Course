import { ApiError, apiClient } from '@/api/client'
import type { Household, Invite } from './types'

const BASE_URL = '/api/v1/households'

/** Devolve `null` (em vez de atirar) quando o utilizador não pertence a nenhum
 * agregado — é um estado normal, não um erro. */
export async function getMyHousehold(): Promise<Household | null> {
  try {
    return await apiClient.get<Household>(`${BASE_URL}/me`)
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null
    throw err
  }
}

export function createHousehold(name: string) {
  return apiClient.post<Household>(BASE_URL, { name })
}

export function leaveHousehold() {
  return apiClient.post<void>(`${BASE_URL}/me/leave`)
}

export function inviteMember(email: string) {
  return apiClient.post<Invite>(`${BASE_URL}/me/invites`, { email })
}

export function listSentInvites() {
  return apiClient.get<Invite[]>(`${BASE_URL}/me/invites`)
}

export function cancelInvite(inviteId: string) {
  return apiClient.delete<void>(`${BASE_URL}/me/invites/${inviteId}`)
}

export function listReceivedInvites() {
  return apiClient.get<Invite[]>(`${BASE_URL}/invites`)
}

export function acceptInvite(inviteId: string) {
  return apiClient.post<Household>(`${BASE_URL}/invites/${inviteId}/accept`)
}

export function declineInvite(inviteId: string) {
  return apiClient.post<void>(`${BASE_URL}/invites/${inviteId}/decline`)
}
