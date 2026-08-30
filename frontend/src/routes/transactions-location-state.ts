import type { TransactionFormValues } from '@/features/transactions/schemas'

// Estado de navegação para abrir /transacoes com o form pré-preenchido (botão
// "Recarregar plafond", ver card-status.tsx). Módulo à parte para não puxar a página toda.
export type TransactionsLocationState = {
  prefillTransaction?: Partial<TransactionFormValues>
}
