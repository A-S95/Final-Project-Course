import { motion, useReducedMotion } from 'motion/react'
import type { ReactNode } from 'react'

// Linha de uma lista: entra com fade + slide (stagger por índice) e levanta-se
// ligeiramente no hover. Substitui o mesmo `motion.div` copiado nas páginas de
// contas, categorias, objetivos, orçamentos e recorrentes. Respeita
// prefers-reduced-motion (sem animação de entrada nem hover).
export function AnimatedListItem({
  index,
  className,
  children,
}: {
  index: number
  className?: string
  children: ReactNode
}) {
  const reduceMotion = useReducedMotion()
  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04, ease: 'easeOut' }}
      whileHover={reduceMotion ? undefined : { y: -2 }}
      className={className}
    >
      {children}
    </motion.div>
  )
}
