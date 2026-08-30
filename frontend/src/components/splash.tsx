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
