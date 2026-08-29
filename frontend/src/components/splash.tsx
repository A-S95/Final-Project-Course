import { motion, useReducedMotion } from 'motion/react'
import { LogoMark } from '@/components/logo'

// Usado nos dois momentos reais de espera da app: a verificação de sessão no
// arranque (AuthProvider/ProtectedRoute) e o carregamento de uma rota lazy
// (Suspense em App.tsx) — substitui o antigo texto simples "A carregar...".
// A moeda "gira" enquanto se espera — motivo óbvio para animação contínua
// (ao contrário de um flip-in de uma vez só, aqui há mesmo algo a decorrer).
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

// Igual à Splash, mas para dentro da área de conteúdo do AppShell (a
// navegação em si — sidebar, topo — já lá está montada e não deve
// desaparecer nem piscar; só o conteúdo por baixo precisa de um indicador
// enquanto uma rota lazy ainda não carregou pela primeira vez).
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
