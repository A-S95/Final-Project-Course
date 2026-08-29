// ISO 4217, restrito às moedas com suporte de formatação testado na UI
// (Intl.NumberFormat aceita qualquer código de 3 letras — esta lista é só
// para o seletor, não uma validação; o backend aceita qualquer código válido).
export const CURRENCIES = ['EUR', 'USD', 'GBP', 'BRL', 'CHF'] as const
export type Currency = (typeof CURRENCIES)[number]
export const CURRENCY_LABELS: Record<Currency, string> = {
  EUR: 'Euro (EUR)',
  USD: 'Dólar americano (USD)',
  GBP: 'Libra esterlina (GBP)',
  BRL: 'Real brasileiro (BRL)',
  CHF: 'Franco suíço (CHF)',
}

export type User = {
  id: string
  email: string
  name: string
  currency: string
  // Decimal do backend chega sempre como string (Pydantic v2 serializa
  // Decimal para string em JSON, não para number — nunca perder precisão).
  monthly_income: string | null
}

export type AuthResponse = {
  access_token: string
  token_type: string
  user: User
}
