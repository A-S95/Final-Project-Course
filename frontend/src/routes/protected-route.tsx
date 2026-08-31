import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { Suspense } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { AppShell } from '@/components/app-shell'
import { ConnectionError, ContentSpinner, Splash } from '@/components/splash'
import { useAuth } from '@/features/auth/use-auth'

// Rota de layout: monta o AppShell uma vez só, o <Outlet/> entra/sai sozinho.
// Antes cada rota embrulhava <ProtectedRoute> individualmente e a sidebar remontava a cada clique.
export function ProtectedRoute() {
  const { status, retrySession } = useAuth()
  const location = useLocation()
  const reduceMotion = useReducedMotion()

  if (status === 'loading') {
    return <Splash />
  }

  if (status === 'connection-error') {
    return <ConnectionError onRetry={retrySession} />
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  return (
    <AppShell>
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={reduceMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={reduceMotion ? undefined : { opacity: 0 }}
          transition={{ duration: reduceMotion ? 0 : 0.2, ease: 'easeOut' }}
          className="flex flex-1 flex-col"
        >
          <Suspense fallback={<ContentSpinner />}>
            <Outlet />
          </Suspense>
        </motion.div>
      </AnimatePresence>
    </AppShell>
  )
}
