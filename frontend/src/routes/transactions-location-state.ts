import type { TransactionFormValues } from '@/features/transactions/schemas'

// Estado passado via `navigate(path, { state })` para abrir /transacoes já
// com o formulário de criação pré-preenchido — usado pelo botão "Recarregar
// plafond" nos cartões de conta (ver features/accounts/card-status.tsx).
// Módulo à parte (em vez de exportado de routes/transactions.tsx) para quem
// só precisa do tipo não puxar a página toda.
export type TransactionsLocationState = {
  prefillTransaction?: Partial<TransactionFormValues>
}
