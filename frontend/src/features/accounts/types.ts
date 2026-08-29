export const ACCOUNT_TYPES = ['BANK', 'WALLET', 'SAVINGS', 'CREDIT_CARD', 'OTHER'] as const
export type AccountType = (typeof ACCOUNT_TYPES)[number]

export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  BANK: 'Banco',
  WALLET: 'Carteira',
  SAVINGS: 'Poupança',
  CREDIT_CARD: 'Cartão de crédito',
  OTHER: 'Outra',
}

export type Account = {
  id: string
  name: string
  type: AccountType
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  initial_balance: string
  current_balance: string
  // Validade do cartão (débito/crédito) e plafond esperado de um pré-pago —
  // ambos opcionais, null quando a conta não é tratada como um cartão.
  card_expiration_date: string | null
  card_plafond: string | null
  created_at: string
  updated_at: string
}

export type AccountInput = {
  name: string
  type: AccountType
  initial_balance: string
  card_expiration_date: string | null
  card_plafond: string | null
}
