import { lazy, Suspense, type ReactNode } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { ErrorBoundary } from '@/components/error-boundary'
import { Splash } from '@/components/splash'
import { AuthProvider } from '@/features/auth/auth-context'
import { ProtectedRoute } from '@/routes/protected-route'

// Uma página por chunk: nenhuma rota carrega o código (nem as dependências
// só suas, como o Recharts do dashboard/histórico) de todas as outras. Os
// exports nomeados (não default) exigem o `.then` a remapear para `default`
// — é o próprio React.lazy que impõe esse formato.
const LoginPage = lazy(() => import('@/routes/login').then((m) => ({ default: m.LoginPage })))
const RegisterPage = lazy(() =>
  import('@/routes/register').then((m) => ({ default: m.RegisterPage })),
)
const DashboardPage = lazy(() =>
  import('@/routes/dashboard').then((m) => ({ default: m.DashboardPage })),
)
const AccountsPage = lazy(() =>
  import('@/routes/accounts').then((m) => ({ default: m.AccountsPage })),
)
const CategoriesPage = lazy(() =>
  import('@/routes/categories').then((m) => ({ default: m.CategoriesPage })),
)
const TransactionsPage = lazy(() =>
  import('@/routes/transactions').then((m) => ({ default: m.TransactionsPage })),
)
const HouseholdPage = lazy(() =>
  import('@/routes/household').then((m) => ({ default: m.HouseholdPage })),
)
const BudgetsPage = lazy(() =>
  import('@/routes/budgets').then((m) => ({ default: m.BudgetsPage })),
)
const RecurringPage = lazy(() =>
  import('@/routes/recurring').then((m) => ({ default: m.RecurringPage })),
)
const GoalsPage = lazy(() => import('@/routes/goals').then((m) => ({ default: m.GoalsPage })))
const LandingPage = lazy(() =>
  import('@/routes/landing').then((m) => ({ default: m.LandingPage })),
)
const HistoryPage = lazy(() =>
  import('@/routes/history').then((m) => ({ default: m.HistoryPage })),
)
const SettingsPage = lazy(() =>
  import('@/routes/settings').then((m) => ({ default: m.SettingsPage })),
)

// Só as rotas públicas (sem sidebar) usam esta transição de página inteira —
// as protegidas têm a sua própria, mais local, dentro do <ProtectedRoute/>
// (ver routes/protected-route.tsx), para a navegação lateral nunca desmontar.
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
