/** Utilitários de navegação por mês — partilhados pelo dashboard (Fase 6) e pelos
 * orçamentos (Fase 8). Sempre em hora local (nunca `toISOString`, que converte
 * para UTC e pode saltar um dia perto da meia-noite). */

export function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

export function addMonths(date: Date, amount: number): Date {
  return new Date(date.getFullYear(), date.getMonth() + amount, 1)
}

/** "YYYY-MM-DD" em hora local — o formato que a API espera no parâmetro `month`. */
export function toIsoDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function monthLabel(date: Date): string {
  // "agosto de 2026" → "Agosto de 2026" (só a primeira letra, não cada palavra).
  const label = new Intl.DateTimeFormat('pt-PT', { month: 'long', year: 'numeric' }).format(date)
  return label.charAt(0).toUpperCase() + label.slice(1)
}

export function isSameMonth(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth()
}

/** "2026-06-01" -> Date local (sem o desvio de fuso do `new Date(string)`). */
export function parseIsoDate(iso: string): Date {
  const [year, month, day] = iso.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/** "2026-06-01" -> "jun 26" (para eixos de gráficos que podem cruzar o ano). */
export function shortMonthLabel(iso: string): string {
  const date = parseIsoDate(iso)
  const month = new Intl.DateTimeFormat('pt-PT', { month: 'short' })
    .format(date)
    .replace('.', '')
  return `${month} ${String(date.getFullYear()).slice(2)}`
}
