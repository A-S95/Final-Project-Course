import { lazy, Suspense, type ComponentType, type ReactNode } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { ErrorBoundary } from '@/components/error-boundary'
import { Splash } from '@/components/splash'
import { AuthProvider } from '@/features/auth/auth-context'
import { ProtectedRoute } from '@/routes/protected-route'

const CHUNK_RELOAD_FLAG = 'chunk-reload'

// Um chunk que falha a carregar é quase sempre um deploy novo: o browser pede um
// ficheiro com um hash que já não existe (404). Recarrega a página uma vez — o guard
// em sessionStorage evita um ciclo de reload se a falha for outra coisa (offline).
function lazyWithReload<T extends ComponentType<object>>(
  factory: () => Promise<{ default: T }>,
) {
  return lazy(() =>
    factory()
      .then((mod) => {
        try {
          sessionStorage.removeItem(CHUNK_RELOAD_FLAG)
        } catch {
          // sessionStorage indisponível (modo privado) — não é crítico.
        }
        return mod
      })
      .catch((err: unknown) => {
        try {
          if (!sessionStorage.getItem(CHUNK_RELOAD_FLAG)) {
            sessionStorage.setItem(CHUNK_RELOAD_FLAG, '1')
            window.location.reload()
            return new Promise<{ default: T }>(() => {}) // nunca resolve; a página vai recarregar
          }
        } catch {
          // ignore
        }
        throw err
      }),
  )
}

// Uma página por chunk. `.then` remapeia export nomeado para `default`, que React.lazy exige.
const LoginPage = lazyWithReload(() => import('@/routes/login').then((m) => ({ default: m.LoginPage })))
const RegisterPage = lazyWithReload(() =>
  import('@/routes/register').then((m) => ({ default: m.RegisterPage })),
)
const DashboardPage = lazyWithReload(() =>
  import('@/routes/dashboard').then((m) => ({ default: m.DashboardPage })),
)
const AccountsPage = lazyWithReload(() =>
  import('@/routes/accounts').then((m) => ({ default: m.AccountsPage })),
)
const CategoriesPage = lazyWithReload(() =>
  import('@/routes/categories').then((m) => ({ default: m.CategoriesPage })),
)
const TransactionsPage = lazyWithReload(() =>
  import('@/routes/transactions').then((m) => ({ default: m.TransactionsPage })),
)
const HouseholdPage = lazyWithReload(() =>
  import('@/routes/household').then((m) => ({ default: m.HouseholdPage })),
)
const BudgetsPage = lazyWithReload(() =>
  import('@/routes/budgets').then((m) => ({ default: m.BudgetsPage })),
)
const RecurringPage = lazyWithReload(() =>
  import('@/routes/recurring').then((m) => ({ default: m.RecurringPage })),
)
const GoalsPage = lazyWithReload(() => import('@/routes/goals').then((m) => ({ default: m.GoalsPage })))
const LandingPage = lazyWithReload(() =>
  import('@/routes/landing').then((m) => ({ default: m.LandingPage })),
)
const HistoryPage = lazyWithReload(() =>
  import('@/routes/history').then((m) => ({ default: m.HistoryPage })),
)
const SettingsPage = lazyWithReload(() =>
  import('@/routes/settings').then((m) => ({ default: m.SettingsPage })),
)

// Só rotas públicas: as protegidas têm a sua própria transição, mais local, em ProtectedRoute.
function PublicPageTransition({ children }: { children: ReactNode }) {
  const location = useLocation()
  const reduceMotion = useReducedMotion()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={reduceMotion ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={reduceMotion ? undefined : { opacity: 0 }}
        transition={{ duration: reduceMotion ? 0 : 0.18, ease: 'easeOut' }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

function AnimatedRoutes() {
  const location = useLocation()

  return (
    <Suspense fallback={<Splash />}>
      <Routes location={location}>
        <Route
          path="/"
          element={
            <PublicPageTransition>
              <LandingPage />
            </PublicPageTransition>
          }
        />
        <Route
          path="/login"
          element={
            <PublicPageTransition>
              <LoginPage />
            </PublicPageTransition>
          }
        />
        <Route
          path="/registar"
          element={
            <PublicPageTransition>
              <RegisterPage />
            </PublicPageTransition>
          }
        />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/contas" element={<AccountsPage />} />
          <Route path="/categorias" element={<CategoriesPage />} />
          <Route path="/transacoes" element={<TransactionsPage />} />
          <Route path="/agregado" element={<HouseholdPage />} />
          <Route path="/orcamentos" element={<BudgetsPage />} />
          <Route path="/recorrentes" element={<RecurringPage />} />
          <Route path="/objetivos" element={<GoalsPage />} />
          <Route path="/historico" element={<HistoryPage />} />
          <Route path="/definicoes" element={<SettingsPage />} />
        </Route>
      </Routes>
    </Suspense>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <AnimatedRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
