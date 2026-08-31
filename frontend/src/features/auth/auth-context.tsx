import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { refreshSession } from '@/api/client'
import { setAccessToken, setSessionExpiredHandler } from '@/api/token-store'
import * as authApi from './api'
import { AuthContext, type AuthStatus } from './context'
import type { User } from './types'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [status, setStatus] = useState<AuthStatus>('loading')

  const runSessionCheck = useCallback(() => {
    let cancelled = false
    // O access token perde-se a um refresh de propósito; recupera-se aqui via cookie.
    refreshSession()
      .then((result) => {
        if (cancelled) return
        setUser(result?.user ?? null)
        setStatus(result ? 'authenticated' : 'unauthenticated')
      })
      .catch(() => {
        // Falha de rede / backend inacessível: não sabemos se a sessão é válida, por
        // isso não deslogamos — mostramos um ecrã de "sem ligação" com opção de repetir.
        if (cancelled) return
        setStatus('connection-error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => runSessionCheck(), [runSessionCheck])

  const retrySession = useCallback(() => {
    setStatus('loading')
    runSessionCheck()
  }, [runSessionCheck])

  // O cliente HTTP avisa quando o refresh token é mesmo rejeitado a meio do uso.
  useEffect(() => {
    setSessionExpiredHandler(() => {
      setUser(null)
      setStatus('unauthenticated')
    })
    return () => setSessionExpiredHandler(null)
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const result = await authApi.loginUser({ email, password })
    setUser(result.user)
    setStatus('authenticated')
  }, [])

  const register = useCallback(async (email: string, password: string, name: string) => {
    const result = await authApi.registerUser({ email, password, name })
    setUser(result.user)
    setStatus('authenticated')
  }, [])

  const logout = useCallback(async () => {
    await authApi.logoutUser().catch(() => undefined)
    setAccessToken(null)
    setUser(null)
    setStatus('unauthenticated')
  }, [])

  const updateUser = useCallback((updated: User) => {
    setUser(updated)
  }, [])

  const value = useMemo(
    () => ({ user, status, login, register, logout, updateUser, retrySession }),
    [user, status, login, register, logout, updateUser, retrySession],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
