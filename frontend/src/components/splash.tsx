import { motion, useReducedMotion } from 'motion/react'
import { LogoMark } from '@/components/logo'

// Verificação de sessão no arranque e carregamento de rota lazy (Suspense).
export function Splash() {
  const reduceMotion = useReducedMotion()

  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-canvas">
      <motion.span
        style={{ perspective: 300 }}
        animate={reduceMotion ? { opacity: 1 } : { rotateY: 360 }}
        transition={{ duration: 1.1, repeat: reduceMotion ? 0 : Infinity, ease: 'linear' }}
      >
        <LogoMark className="h-10 w-10" />
      </motion.span>
      <span className="text-sm text-ink-subtle">A carregar...</span>
    </main>
  )
}

// Arranque falhou a ligar ao backend (rede, ou a Render a acordar) — sem saber se
// a sessão é válida. Distinto do login: aqui o problema é a ligação, não as credenciais.
export function ConnectionError({ onRetry }: { onRetry: () => void }) {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-canvas px-6 text-center">
      <LogoMark className="h-10 w-10 opacity-60" />
      <div>
        <p className="font-medium text-ink">Sem ligação ao servidor</p>
        <p className="mt-1 text-sm text-ink-subtle">
          Não foi possível ligar. Verifica a ligação à internet e tenta de novo.
        </p>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="rounded-xl bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition hover:bg-accent-strong"
      >
        Tentar novamente
      </button>
    </main>
  )
}

// Como a Splash, mas só na área de conteúdo: a sidebar do AppShell não deve piscar.
export function ContentSpinner() {
  const reduceMotion = useReducedMotion()

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 py-24">
      <motion.span
        style={{ perspective: 300 }}
        animate={reduceMotion ? { opacity: 1 } : { rotateY: 360 }}
        transition={{ duration: 1.1, repeat: reduceMotion ? 0 : Infinity, ease: 'linear' }}
      >
        <LogoMark className="h-8 w-8" />
      </motion.span>
      <span className="text-sm text-ink-subtle">A carregar...</span>
    </div>
  )
}
