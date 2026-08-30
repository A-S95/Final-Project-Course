export const TRANSACTION_TYPES = ['INCOME', 'EXPENSE', 'TRANSFER'] as const
export type TransactionType = (typeof TRANSACTION_TYPES)[number]

export const TRANSACTION_TYPE_LABELS: Record<TransactionType, string> = {
  INCOME: 'Receita',
  EXPENSE: 'Despesa',
  TRANSFER: 'Transferência',
}

export type Transaction = {
  id: string
  account_id: string
  destination_account_id: string | null
  category_id: string | null
  type: TransactionType
  // Decimal do backend chega sempre como string — ver features/auth/types.ts.
  amount: string
  description: string | null
  date: string
  // Despesa do agregado (ver ARCHITECTURE.md secção 8); sem efeito fora de um agregado.
  is_shared: boolean
  // null = sem recibo. Ficheiro pede-se à parte com getReceipt() (protegido).
  receipt_content_type: string | null
  created_at: string
  updated_at: string
}

export type TransactionInput = {
  account_id: string
  destination_account_id: string | null
  category_id: string | null
  type: TransactionType
  amount: string
  description: string | null
  date: string
  is_shared: boolean
}

export type TransactionFilters = {
  account_id?: string
  category_id?: string
  type?: TransactionType
  date_from?: string
  date_to?: string
}
