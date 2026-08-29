import {
  ArrowLeftRight,
  LayoutDashboard,
  LineChart,
  LogOut,
  type LucideIcon,
  Menu,
  PiggyBank,
  Repeat,
  Settings,
  Tags,
  Target,
  Users,
  Wallet,
  X,
} from 'lucide-react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { type ReactNode, useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LogoMark } from '@/components/logo'
import { ThemeToggle } from '@/components/theme-toggle'
import { useAuth } from '@/features/auth/use-auth'

type NavItem = { path: string; label: string; icon: LucideIcon }

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard', label: 'Painel', icon: LayoutDashboard },
  { path: '/contas', label: 'Contas', icon: Wallet },
  { path: '/categorias', label: 'Categorias', icon: Tags },
  { path: '/transacoes', label: 'Transações', icon: ArrowLeftRight },
  { path: '/orcamentos', label: 'Orçamentos', icon: PiggyBank },
  { path: '/recorrentes', label: 'Recorrentes', icon: Repeat },
  { path: '/objetivos', label: 'Objetivos', icon: Target },
  { path: '/historico', label: 'Histórico', icon: LineChart },
  { path: '/agregado', label: 'Agregado', icon: Users },
  { path: '/definicoes', label: 'Definições', icon: Settings },
]

function initials(name: string) {
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] ?? ''
  const last = parts.length > 1 ? (parts[parts.length - 1]?.[0] ?? '') : ''
  return (first + last).toUpperCase()
}

function Brand() {
  const reduceMotion = useReducedMotion()

  // O AppShell (rota de layout) só monta uma vez por sessão autenticada —
  // não a cada navegação — por isso o flip-in de entrada é seguro aqui, não
  // se repete a cada clique na sidebar.
  return (
    <Link to="/dashboard" className="font-display inline-flex items-center gap-2 font-semibold text-ink">
      <motion.span
        style={{ perspective: 300 }}
        initial={reduceMotion ? false : { rotateY: -110, opacity: 0 }}
        animate={{ rotateY: 0, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <LogoMark className="h-8 w-8 shrink-0" />
      </motion.span>
      <span className="text-base">CentiSible</span>
    </Link>
  )
}

function NavLink({ item, onNavigate }: { item: NavItem; onNavigate?: () => void }) {
  const location = useLocation()
  const active = location.pathname === item.path
  const Icon = item.icon

  return (
    <Link
      to={item.path}
      onClick={onNavigate}
      aria-current={active ? 'page' : undefined}
      className={`group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
        active ? 'text-ink' : 'text-ink-muted hover:bg-surface-hover hover:text-ink'
      }`}
    >
      {active && (
        <motion.span
          layoutId="nav-active-pill"
          className="absolute inset-0 rounded-lg bg-accent/12"
          transition={{ type: 'spring', stiffness: 500, damping: 40 }}
        />
      )}
      <Icon
        className={`relative h-[18px] w-[18px] shrink-0 transition-colors ${active ? 'text-accent' : 'text-ink-subtle group-hover:text-ink-muted'}`}
      />
      <span className="relative">{item.label}</span>
    </Link>
  )
}

function UserFooter({ onNavigate }: { onNavigate?: () => void }) {
  const { user, logout } = useAuth()
  if (!user) return null

  return (
    <div className="flex items-center gap-2 border-t border-border px-3 py-3">
      <Link
        to="/definicoes"
        onClick={onNavigate}
        className="flex min-w-0 flex-1 items-center gap-2.5 rounded-lg px-1.5 py-1 transition-colors hover:bg-surface-hover"
      >
        <span className="brand-gradient flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white">
          {initials(user.name)}
        </span>
        <span className="min-w-0">
          <span className="block truncate text-sm font-medium text-ink">{user.name}</span>
          <span className="block truncate text-xs text-ink-subtle">{user.email}</span>
        </span>
      </Link>
      <ThemeToggle />
      <button
        type="button"
        onClick={() => logout()}
        title="Terminar sessão"
        aria-label="Terminar sessão"
        className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
      >
        <LogOut className="h-4 w-4" />
      </button>
    </div>
  )
}

function DesktopSidebar() {
  return (
    <aside className="sticky top-0 hidden h-svh w-64 shrink-0 flex-col border-r border-border bg-surface md:flex">
      <div className="px-4 py-5">
        <Brand />
      </div>
      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.path} item={item} />
        ))}
      </nav>
      <UserFooter />
    </aside>
  )
}

function MobileTopBar({ onOpen }: { onOpen: () => void }) {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-border bg-surface px-4 py-3 md:hidden">
      <Brand />
      <button
        type="button"
        onClick={onOpen}
        aria-label="Abrir menu"
        className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink"
      >
        <Menu className="h-5 w-5" />
      </button>
    </header>
  )
}

function MobileDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const reduceMotion = useReducedMotion()

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-black/40 md:hidden"
          />
          <motion.div
            initial={reduceMotion ? { opacity: 0 } : { x: '-100%' }}
            animate={reduceMotion ? { opacity: 1 } : { x: 0 }}
            exit={reduceMotion ? { opacity: 0 } : { x: '-100%' }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-surface shadow-xl md:hidden"
          >
            <div className="flex items-center justify-between px-4 py-5">
              <Brand />
              <button
                type="button"
                onClick={onClose}
                aria-label="Fechar menu"
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border text-ink-muted hover:bg-surface-hover hover:text-ink"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3">
              {NAV_ITEMS.map((item) => (
                <NavLink key={item.path} item={item} onNavigate={onClose} />
              ))}
            </nav>
            <UserFooter onNavigate={onClose} />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export function AppShell({ children }: { children: ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const location = useLocation()

  // Fecha o drawer sempre que a rota muda (ex: utilizador navegou por outro
  // meio, como o botão "voltar" do browser, sem passar por onNavigate).
  useEffect(() => {
    setDrawerOpen(false)
  }, [location.pathname])

  return (
    <div className="flex min-h-svh bg-canvas">
      <DesktopSidebar />
      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <MobileTopBar onOpen={() => setDrawerOpen(true)} />
        {children}
      </div>
    </div>
  )
}
