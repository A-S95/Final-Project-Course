import { motion, useReducedMotion } from 'motion/react'
import type { ReactNode } from 'react'

// Cabeçalho comum a todas as páginas internas — título + subtítulo opcional
// + zona de ações à direita (ex: botão principal da página). A navegação
// (voltar/trocar de secção) e o alternador de tema já vivem no `AppShell`
// (barra lateral), por isso este cabeçalho já não precisa de os repetir.
export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string
  subtitle?: string
  actions?: ReactNode
}) {
  const reduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="flex flex-wrap items-center justify-between gap-3"
    >
      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </motion.div>
  )
}
