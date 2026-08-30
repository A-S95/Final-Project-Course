import { Link, Navigate } from 'react-router-dom'
import { motion, useReducedMotion } from 'motion/react'
import { ArrowRight } from 'lucide-react'
import { Logo, LogoMark } from '@/components/logo'
import { AnimatedNumber } from '@/components/animated-number'
import { buttonVariants } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { cn } from '@/lib/utils'
import { useAuth } from '@/features/auth/use-auth'

const formatEur = (value: number) =>
  new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(value)

// Seta que escapa no hover, subtil, só para sentir-se responsivo.
function CtaLink({
  to,
  children,
  className,
}: {
  to: string
  children: string
  className: string
}) {
  return (
    <Link to={to} className={cn(className, 'group')}>
      {children}
      <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
    </Link>
  )
}

// A moeda "assenta" ao carregar a página, uma vez só, nunca se repete.
function AnimatedLogo() {
  const reduceMotion = useReducedMotion()

  return (
    <span className="font-display flex items-center gap-2 text-lg font-semibold tracking-tight text-ink">
      <motion.span
        style={{ perspective: 300 }}
        initial={reduceMotion ? false : { rotateY: -110, opacity: 0 }}
        animate={{ rotateY: 0, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <LogoMark className="h-7 w-7" />
      </motion.span>
      CentiSible
    </span>
  )
}

function Nav() {
  return (
    <header className="sticky top-0 z-20 border-b border-border/60 bg-canvas/70 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <AnimatedLogo />
        <nav className="flex items-center gap-3 text-sm">
          <ThemeToggle />
          <Link to="/login" className="px-3 py-2 text-ink-muted hover:text-ink">
            Entrar
          </Link>
          <Link to="/registar" className={buttonVariants({ size: 'sm' })}>
            Criar conta grátis
          </Link>
        </nav>
      </div>
    </header>
  )
}

type Row = { label: string; place: string; amount: string; kind: 'income' | 'expense' }

const LEDGER_ROWS: Row[] = [
  { label: 'Ordenado', place: 'Salário', amount: '+1 200,00 €', kind: 'income' },
  { label: 'Renda', place: 'Casa', amount: '-420,00 €', kind: 'expense' },
  { label: 'Alimentação', place: 'Continente', amount: '-38,20 €', kind: 'expense' },
  { label: 'Transporte', place: 'Combustível', amount: '-45,00 €', kind: 'expense' },
]

function LedgerCard() {
  const reduceMotion = useReducedMotion()

  return (
    <div className="relative w-full max-w-sm">
      {/* Brilho a flutuar atrás do cartão — assinatura discreta da secção,
          desligado sem animação: fica só um resplendor estático. */}
      <motion.div
        aria-hidden="true"
        className="absolute -inset-6 -z-10 rounded-[2rem] bg-accent/25 blur-3xl"
        animate={reduceMotion ? undefined : { y: [0, -14, 0], opacity: [0.5, 0.75, 0.5] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, y: 24, rotate: -2 }}
        animate={{ opacity: 1, y: 0, rotate: -2 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="rounded-2xl border border-border bg-surface-raised p-5 shadow-[0_30px_60px_-20px_rgba(101,82,245,0.35)]"
      >
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div>
            <p className="text-xs text-ink-subtle">Agosto 2026</p>
            <p className="font-display text-lg font-semibold text-ink">
              <AnimatedNumber value={1960.28} formatter={formatEur} />
            </p>
          </div>
          <span className="rounded-full bg-accent-soft px-2.5 py-1 text-xs font-medium text-accent-strong dark:text-accent">
            Individual
          </span>
        </div>
        <ul className="flex flex-col">
          {LEDGER_ROWS.map((row, index) => (
            <motion.li
              key={row.label}
              initial={reduceMotion ? false : { opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: 0.3 + index * 0.12, ease: 'easeOut' }}
              className="flex items-center justify-between border-b border-border py-3 text-sm last:border-0"
            >
              <div>
                <p className="font-medium text-ink">{row.label}</p>
                <p className="text-xs text-ink-subtle">{row.place}</p>
              </div>
              <span
                className={`tabular-nums font-medium ${row.kind === 'income' ? 'text-emerald-500' : 'text-ink-muted'}`}
              >
                {row.amount}
              </span>
            </motion.li>
          ))}
        </ul>
      </motion.div>
    </div>
  )
}

function Hero() {
  const reduceMotion = useReducedMotion()
  const fadeUp = (delay: number) => ({
    initial: reduceMotion ? false : { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5, delay, ease: 'easeOut' as const },
  })

  return (
    <section className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:py-24">
      <div className="flex flex-col gap-6">
        <motion.span
          {...fadeUp(0)}
          className="w-fit rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium text-ink-muted"
        >
          Gestão financeira pessoal
        </motion.span>
        <motion.h1
          {...fadeUp(0.08)}
          className="font-display text-4xl font-semibold leading-[1.05] tracking-tight text-ink sm:text-5xl lg:text-6xl"
        >
          O teu dinheiro,
          <br />
          <motion.span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage:
                'linear-gradient(90deg, var(--accent) 0%, var(--accent-strong) 35%, var(--accent-amber) 50%, var(--accent-strong) 65%, var(--accent) 100%)',
              backgroundSize: '250% 100%',
            }}
            animate={reduceMotion ? undefined : { backgroundPositionX: ['0%', '100%'] }}
            transition={{ duration: 6, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
          >
            à vista.
          </motion.span>
        </motion.h1>
        <motion.p {...fadeUp(0.16)} className="max-w-md text-lg text-ink-muted">
          Sabes sempre quanto tens, quanto deves e quanto falta para o próximo objetivo. Nada de
          folhas de cálculo às 23h a tentar perceber para onde foi o dinheiro.
        </motion.p>
        <motion.div {...fadeUp(0.24)} className="flex flex-wrap items-center gap-3">
          <CtaLink to="/registar" className={buttonVariants({ size: 'lg' })}>
            Criar conta grátis
          </CtaLink>
          <Link to="/login" className={buttonVariants({ size: 'lg', variant: 'outline' })}>
            Já tenho conta
          </Link>
        </motion.div>
        <motion.p {...fadeUp(0.3)} className="text-sm text-ink-subtle">
          Grátis, sem cartão de crédito.
        </motion.p>
      </div>
      <div className="flex justify-center lg:justify-end">
        <LedgerCard />
      </div>
    </section>
  )
}

type Feature = { title: string; description: string }

const FEATURES: Feature[] = [
  {
    title: 'Dashboard claro',
    description:
      'Vês o saldo, o que entrou e o que saiu num relance, e recebes um aviso assim que algo fugir do costume.',
  },
  {
    title: 'Orçamentos por categoria',
    description:
      'Defines um limite por categoria e vês a barra encher-se ao longo do mês. Sabes que estás perto do limite antes de o estourares, não depois de já ser tarde.',
  },
  {
    title: 'Objetivos com prazo',
    description:
      'Dá um nome e um prazo ao teu próximo objetivo, seja uma viagem, um carro ou um fundo de emergência, e vê o progresso crescer a cada depósito.',
  },
]

function Features() {
  const reduceMotion = useReducedMotion()

  return (
    <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-24">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        {FEATURES.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={reduceMotion ? false : { opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            whileHover={reduceMotion ? undefined : { y: -6 }}
            transition={{ duration: 0.5, delay: index * 0.1, ease: 'easeOut' }}
            className="rounded-2xl border border-border bg-surface-raised p-6 transition-shadow duration-300 hover:border-accent/40 hover:shadow-[0_20px_40px_-24px_var(--accent)]"
          >
            <h3 className="font-display text-lg font-semibold text-ink">{feature.title}</h3>
            <p className="mt-2 text-sm text-ink-muted">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  )
}

function HouseholdMerge() {
  const reduceMotion = useReducedMotion()

  return (
    <div className="flex flex-col items-center gap-3 rounded-2xl border border-border bg-surface-raised p-6">
      <motion.div
        initial={reduceMotion ? false : { opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.4 }}
        className="grid w-full grid-cols-2 gap-3 text-sm"
      >
        <motion.div
          initial={reduceMotion ? false : { x: 0 }}
          whileInView={reduceMotion ? {} : { x: 14 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.6, delay: 0.3, ease: 'easeInOut' }}
          className="rounded-xl border border-border bg-surface px-4 py-3"
        >
          <p className="text-xs text-ink-subtle">Antonio</p>
          <p className="font-medium text-ink">Renda</p>
          <p className="tabular-nums text-ink-muted">-420,00 €</p>
        </motion.div>
        <motion.div
          initial={reduceMotion ? false : { x: 0 }}
          whileInView={reduceMotion ? {} : { x: -14 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.6, delay: 0.3, ease: 'easeInOut' }}
          className="rounded-xl border border-border bg-surface px-4 py-3"
        >
          <p className="text-xs text-ink-subtle">Teresa</p>
          <p className="font-medium text-ink">Renda</p>
          <p className="tabular-nums text-ink-muted">-420,00 €</p>
        </motion.div>
      </motion.div>
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, y: -6 }}
        whileInView={
          reduceMotion ? { opacity: 1 } : { opacity: 1, y: [0, 4, 0] }
        }
        viewport={{ once: true, margin: '-80px' }}
        transition={
          reduceMotion
            ? { duration: 0.4 }
            : { opacity: { duration: 0.4, delay: 1 }, y: { duration: 1.4, delay: 1.4, repeat: Infinity, ease: 'easeInOut' } }
        }
        className="text-ink-subtle"
      >
        ↓
      </motion.div>
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, scale: 0.95 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.4, delay: reduceMotion ? 0 : 1.1 }}
        className="w-full rounded-xl border border-accent/40 bg-accent-soft px-4 py-3 text-sm"
      >
        <p className="text-xs font-medium text-accent-strong dark:text-accent">
          Agregado familiar
        </p>
        <p className="font-medium text-ink">Renda · partilhada</p>
        <p className="tabular-nums text-ink-muted">-420,00 € — não -840,00 €</p>
      </motion.div>
    </div>
  )
}

function HouseholdSection() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-24">
      <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
        <div className="flex flex-col gap-4">
          <h2 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Vive a dois. Sem contas a dobrar.
          </h2>
          <p className="text-lg text-ink-muted">
            Tu tens as tuas contas e o teu par tem as dele, mas a renda, a luz e a água são
            despesas de casa. Marca-as como partilhadas e o agregado conta-as uma única vez,
            nunca a dobrar, mesmo que cada um organize as categorias à sua maneira.
          </p>
          <Link
            to="/registar"
            className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'w-fit')}
          >
            Experimentar com o meu agregado
          </Link>
        </div>
        <HouseholdMerge />
      </div>
    </section>
  )
}

function FinalCta() {
  const reduceMotion = useReducedMotion()

  return (
    <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-24">
      <motion.div
        initial={reduceMotion ? false : { opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center gap-6 rounded-3xl border border-border bg-surface-raised px-6 py-16 text-center"
      >
        <h2 className="font-display max-w-xl text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
          Deixa de adivinhar quanto sobra até ao fim do mês.
        </h2>
        <p className="text-sm text-ink-subtle">Demora menos de um minuto a criar conta.</p>
        <CtaLink to="/registar" className={buttonVariants({ size: 'lg' })}>
          Criar conta grátis
        </CtaLink>
      </motion.div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 px-4 py-8 text-sm text-ink-subtle sm:flex-row sm:justify-between sm:px-6">
        <Logo markClassName="h-7 w-7" textClassName="text-lg tracking-tight" />
        <p>Um projeto pessoal, construído a pensar no dia a dia de quem o usa.</p>
      </div>
    </footer>
  )
}

export function LandingPage() {
  const { status } = useAuth()

  if (status === 'authenticated') {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="min-h-svh bg-canvas">
      <Nav />
      <main>
        <Hero />
        <Features />
        <HouseholdSection />
        <FinalCta />
      </main>
      <Footer />
    </div>
  )
}
