import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { Suspense } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { AppShell } from '@/components/app-shell'
import { ContentSpinner, Splash } from '@/components/splash'
import { useAuth } from '@/features/auth/use-auth'

// Rota de layout (React Router "nested routes"): monta o AppShell uma única
// vez e mantém-no montado enquanto o utilizador navega entre páginas
// protegidas — só o <Outlet/> (a página em si) entra/sai. Antes, cada rota
// embrulhava individualmente <ProtectedRoute>{children}</ProtectedRoute>,
// o que fazia a sidebar toda desmontar e remontar a cada clique no menu:
// lida-se com isso aqui para a navegação parecer suave em vez de "piscar".
export function ProtectedRoute() {
  const { status } = useAuth()
  const location = useLocation()
  const reduceMotion = useReducedMotion()

  if (status === 'loading') {
    return <Splash />
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
