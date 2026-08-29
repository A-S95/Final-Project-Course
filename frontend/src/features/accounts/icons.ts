import { CreditCard, Landmark, PiggyBank, Wallet, type LucideIcon } from 'lucide-react'
import type { AccountType } from './types'

// Partilhado entre routes/accounts.tsx e routes/dashboard.tsx — um só sítio
// para a escolha de ícone por tipo de conta.
export const ACCOUNT_TYPE_ICONS: Record<AccountType, LucideIcon> = {
  BANK: Landmark,
  WALLET: Wallet,
  SAVINGS: PiggyBank,
  CREDIT_CARD: CreditCard,
  OTHER: Wallet,
}
