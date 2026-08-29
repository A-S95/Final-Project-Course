import { motion, useReducedMotion } from 'motion/react'
import { Link } from 'react-router-dom'
import { ThemeToggle } from '@/components/theme-toggle'

// Cabeçalho comum a todas as páginas internas (não o dashboard, que tem a
// sua própria navegação completa) — título + alternador de tema + link de
// regresso. Usado em vez de repetir o mesmo bloco em 9 ficheiros diferentes.
export function PageHeader({ title }: { title: string }) {
  const reduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="flex items-center justify-between"
    >
      <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">{title}</h1>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <Link to="/dashboard" className="text-sm text-ink-muted underline hover:text-ink">
          Voltar ao painel
        </Link>
      </div>
    </motion.div>
  )
}
