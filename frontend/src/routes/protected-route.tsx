import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Splash } from '@/components/splash'
import { useAuth } from '@/features/auth/use-auth'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return <Splash />
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  return <>{children}</>
}
