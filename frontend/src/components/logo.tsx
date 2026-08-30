import { useId } from 'react'

// "C" + gráfico + moeda = CentiSible (ver logotipostyle.png). `useId` evita
// ids de gradiente colididos quando a marca aparece montada duas vezes.
export function LogoMark({ className = 'h-8 w-8' }: { className?: string }) {
  const gradientId = useId()

  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <defs>
        <linearGradient id={gradientId} x1="16" y1="4" x2="16" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="var(--accent)" />
          <stop offset="1" stopColor="var(--accent-strong)" />
        </linearGradient>
      </defs>
      {/* Arco, não círculo tracejado: controla onde fica a abertura do "C". */}
      <path
        d="M 24.70 21.87 A 10.5 10.5 0 1 1 24.70 10.13"
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth="6.5"
        strokeLinecap="round"
      />
      {/* Gráfico de crescimento, dentro do "C". */}
      <rect x="13.2" y="19" width="1.8" height="3.5" rx="0.8" fill={`url(#${gradientId})`} />
      <rect x="15.6" y="17" width="1.8" height="5.5" rx="0.8" fill={`url(#${gradientId})`} />
      <rect x="18.0" y="14.5" width="1.8" height="8" rx="0.8" fill={`url(#${gradientId})`} />
      <rect x="20.4" y="12" width="1.8" height="10.5" rx="0.8" fill={`url(#${gradientId})`} />
      {/* A moeda — o "centi" do nome. */}
      <circle cx="12.3" cy="12.5" r="1.7" fill="var(--accent-amber)" />
    </svg>
  )
}

export function Logo({
  className = '',
  markClassName = 'h-8 w-8',
  textClassName = 'text-base',
}: {
  className?: string
  markClassName?: string
  textClassName?: string
}) {
  return (
    <span
      className={`font-display inline-flex items-center gap-2 font-semibold text-ink ${className}`}
    >
      <LogoMark className={markClassName} />
      <span className={textClassName}>CentiSible</span>
    </span>
  )
}
