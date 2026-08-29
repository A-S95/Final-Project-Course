import { motion, useReducedMotion } from 'motion/react'

// Usado nos dois momentos reais de espera da app: a verificação de sessão no
// arranque (AuthProvider/ProtectedRoute) e o carregamento de uma rota lazy
// (Suspense em App.tsx) — substitui o antigo texto simples "A carregar...".
export function Splash() {
  const reduceMotion = useReducedMotion()

  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-canvas">
      <motion.span
        animate={
          reduceMotion
            ? { opacity: 1 }
            : { scale: [0.85, 1.05, 0.85], opacity: [0.6, 1, 0.6] }
        }
        transition={{ duration: 1.4, repeat: reduceMotion ? 0 : Infinity, ease: 'easeInOut' }}
        className="brand-gradient flex h-10 w-10 items-center justify-center rounded-xl text-lg font-bold text-white"
      >
        F
      </motion.span>
      <span className="text-sm text-ink-subtle">A carregar...</span>
    </main>
  )
}
