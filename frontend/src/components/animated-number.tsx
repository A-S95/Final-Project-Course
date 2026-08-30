import { useEffect, useState } from 'react'
import { useMotionValue, useReducedMotion, useSpring } from 'motion/react'

// Qualquer valor monetário conta a subir (spring) a partir de 0, em vez de aparecer já preenchido.
export function AnimatedNumber({
  value,
  formatter,
  className,
}: {
  value: number
  formatter: (value: number) => string
  className?: string
}) {
  const reduceMotion = useReducedMotion()
  const motionValue = useMotionValue(0)
  // restDelta pequeno: a margem por omissão podia parar a alguns cêntimos do valor final.
  const spring = useSpring(motionValue, { stiffness: 110, damping: 24, mass: 0.6, restDelta: 0.005 })
  const [display, setDisplay] = useState(() => formatter(0))

  useEffect(() => {
    if (reduceMotion) return
    motionValue.set(value)
  }, [value, reduceMotion, motionValue])

  useEffect(() => {
    if (reduceMotion) return
    return spring.on('change', (latest) => setDisplay(formatter(latest)))
  }, [spring, formatter, reduceMotion])

  // Sem animação: valor derivado direto das props, sem estado/efeito.
  if (reduceMotion) {
    return <span className={className}>{formatter(value)}</span>
  }

  return <span className={className}>{display}</span>
}
