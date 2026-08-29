import { useEffect, useState } from 'react'
import { useMotionValue, useReducedMotion, useSpring } from 'motion/react'

/**
 * Assinatura de "atenção ao pormenor" usada em toda a app: qualquer valor
 * monetário conta a subir (spring, não linear) a partir de 0 quando aparece,
 * e desliza suavemente para o novo valor quando muda (ex: trocar de mês).
 * Sem isto os números só "aparecem" já preenchidos — reforça a proposta da
 * landing ("o teu dinheiro, à vista") em vez de ser só decorativo.
 */
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
  // restDelta pequeno: por omissão o spring considera-se "parado" com uma
  // margem que pode deixar o valor final a alguns cêntimos de distância —
  // visível como um total que nunca bate certo com os cartões abaixo.
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

  // Sem animação (preferência de acessibilidade): o valor é sempre derivado
  // diretamente das props, sem passar por estado/efeito nenhum.
  if (reduceMotion) {
    return <span className={className}>{formatter(value)}</span>
  }

  return <span className={className}>{display}</span>
}
