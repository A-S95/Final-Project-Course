// Sempre em hora local, nunca toISOString (converte para UTC, pode saltar um dia).

export function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

export function addMonths(date: Date, amount: number): Date {
  return new Date(date.getFullYear(), date.getMonth() + amount, 1)
}

/** Último dia do mês de `date` (dia 0 do mês seguinte = último dia deste). */
export function endOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0)
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

/** "2026-09-01" -> "1 set" (dia + mês abreviado, para listas compactas). */
export function shortDayMonthLabel(iso: string): string {
  const date = parseIsoDate(iso)
  const month = new Intl.DateTimeFormat('pt-PT', { month: 'short' }).format(date).replace('.', '')
  return `${date.getDate()} ${month}`
}

/** Dias entre hoje e `iso` (negativo se já passou). Só a data conta, sem hora. */
export function daysUntil(iso: string): number {
  const today = startOfDay(new Date())
  const target = startOfDay(parseIsoDate(iso))
  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
}

/** "2026-08-29" -> "Hoje" / "Ontem" / "25 de agosto" (ano só se não for o atual). */
export function dayGroupLabel(iso: string): string {
  const diff = daysUntil(iso)
  if (diff === 0) return 'Hoje'
  if (diff === -1) return 'Ontem'

  const date = parseIsoDate(iso)
  const sameYear = date.getFullYear() === new Date().getFullYear()
  const label = new Intl.DateTimeFormat('pt-PT', {
    day: 'numeric',
    month: 'long',
    year: sameYear ? undefined : 'numeric',
  }).format(date)
  return label
}

function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}
