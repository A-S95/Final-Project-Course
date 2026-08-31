import { createContext } from 'react'
import type { User } from './types'

// 'connection-error': não conseguimos falar com o backend no arranque — distinto de
// 'unauthenticated', onde o backend respondeu e disse que não há sessão.
export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated' | 'connection-error'

export type AuthContextValue = {
  user: User | null
  status: AuthStatus
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => void
  /** Repetir a verificação de sessão do arranque (usado no ecrã de "sem ligação"). */
  retrySession: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
