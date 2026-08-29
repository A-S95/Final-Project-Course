import { useMemo, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import type { TransactionsLocationState } from '@/routes/transactions-location-state'
import type { Account } from './types'

const EXPIRATION_WARNING_DAYS = 30

// Mesma regra do backend (insights_service._CARD_EXPIRATION_WARNING_DAYS) —
// mostrado aqui como feedback imediato no cartão, sem esperar pelo alerta
// no painel principal.
export function CardStatus({
  account,
  currency,
  formatMoney,
}: {
  account: Account
  currency: string
  formatMoney: (value: string, currency: string) => string
}) {
  // `Date.now()` é impuro — calculado uma vez por montagem (como o padrão já
  // usado em routes/dashboard.tsx para "hoje"), granularidade ao dia chega.
  const now = useMemo(() => new Date().getTime(), [])
  const navigate = useNavigate()
  const badges: ReactNode[] = []

  if (account.card_expiration_date) {
    const daysLeft = Math.floor(
      (new Date(account.card_expiration_date).getTime() - now) / (1000 * 60 * 60 * 24),
    )
    if (daysLeft < 0) {
      badges.push(
        <span key="exp" className="text-xs font-medium text-red-500">
          Cartão expirado
        </span>,
      )
    } else if (daysLeft <= EXPIRATION_WARNING_DAYS) {
      badges.push(
        <span key="exp" className="text-xs font-medium text-amber-500">
          Expira em {daysLeft} dia{daysLeft !== 1 ? 's' : ''}
        </span>,
      )
    } else {
      badges.push(
        <span key="exp" className="text-xs text-ink-muted">
          Válido até{' '}
          {new Date(account.card_expiration_date).toLocaleDateString('pt-PT', {
            month: '2-digit',
            year: 'numeric',
          })}
        </span>,
      )
    }
  }

  if (account.card_plafond) {
    const balance = Number(account.current_balance)
    const plafond = Number(account.card_plafond)
    const pct = plafond > 0 ? Math.min(100, Math.max(0, (balance / plafond) * 100)) : 0
    const below = balance < plafond
    const missing = (plafond - balance).toFixed(2)

    badges.push(
      <div key="plafond" className="flex flex-col gap-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className={below ? 'font-medium text-amber-500' : 'text-ink-muted'}>
            Plafond {formatMoney(account.card_plafond, currency)}
          </span>
          {below && <span className="font-medium text-amber-500">Abaixo do plafond</span>}
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
          <div
            className={`h-full rounded-full ${below ? 'bg-amber-500' : 'bg-accent'}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        {below && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="mt-0.5 self-start"
            onClick={(e) => {
              // O crachá vive dentro de cartões clicáveis (ex: linha de conta
              // com "Editar"/"Eliminar" por baixo) — sem isto, o clique
              // também dispararia o que estiver à volta.
              e.stopPropagation()
              const state: TransactionsLocationState = {
                prefillTransaction: {
                  account_id: account.id,
                  type: 'INCOME',
                  amount: missing,
                  description: 'Recarga de plafond',
                },
              }
              navigate('/transacoes', { state })
            }}
          >
            Recarregar plafond
          </Button>
        )}
      </div>,
    )
  }

  if (badges.length === 0) {
    return null
  }

  return <div className="flex flex-col gap-1.5">{badges}</div>
}
