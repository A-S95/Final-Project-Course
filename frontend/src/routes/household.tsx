import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { ApiError } from '@/api/client'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import * as householdsApi from '@/features/households/api'
import type { Household, Invite } from '@/features/households/types'

function errorMessage(err: unknown, fallback: string) {
  return err instanceof ApiError ? err.message : fallback
}

function ReceivedInvites({ invites }: { invites: Invite[] }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['household'] })
    queryClient.invalidateQueries({ queryKey: ['received-invites'] })
    queryClient.invalidateQueries({ queryKey: ['dashboard'] })
  }

  const acceptMutation = useMutation({
    mutationFn: householdsApi.acceptInvite,
    onSuccess: invalidate,
    onError: (err) => setError(errorMessage(err, 'Não foi possível aceitar o convite.')),
  })
  const declineMutation = useMutation({
    mutationFn: householdsApi.declineInvite,
    onSuccess: invalidate,
    onError: (err) => setError(errorMessage(err, 'Não foi possível recusar o convite.')),
  })

  if (invites.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Convites recebidos</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {invites.map((invite) => (
          <div
            key={invite.id}
            className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border p-3"
          >
            <div className="text-sm">
              <p className="font-medium">{invite.household_name}</p>
              <p className="text-ink-muted">
                Convite de {invite.invited_by_name}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                disabled={acceptMutation.isPending}
                onClick={() => acceptMutation.mutate(invite.id)}
              >
                Aceitar
              </Button>
              <Button
                size="sm"
                variant="outline"
                disabled={declineMutation.isPending}
                onClick={() => declineMutation.mutate(invite.id)}
              >
                Recusar
              </Button>
            </div>
          </div>
        ))}
        {error && <p className="text-sm text-red-600">{error}</p>}
      </CardContent>
    </Card>
  )
}

function CreateHouseholdCard() {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)

  const createMutation = useMutation({
    mutationFn: () => householdsApi.createHousehold(name.trim()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['household'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
    onError: (err) => setError(errorMessage(err, 'Não foi possível criar o agregado.')),
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Criar um agregado familiar</CardTitle>
      </CardHeader>
      <CardContent>
        <form
          className="flex flex-col gap-3"
          onSubmit={(e) => {
            e.preventDefault()
            setError(null)
            if (name.trim()) createMutation.mutate()
          }}
        >
          <p className="text-sm text-ink-muted">
            Junta as tuas finanças às de outra pessoa. Cada um mantém as suas contas e transações
            privadas — o agregado só soma os totais nas vistas partilhadas.
          </p>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="household-name">Nome do agregado</Label>
            <Input
              id="household-name"
              autoComplete="off"
              placeholder="Ex: Família Santos"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div>
            <Button type="submit" disabled={!name.trim() || createMutation.isPending}>
              {createMutation.isPending ? 'A criar...' : 'Criar agregado'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

function InviteForm() {
  const queryClient = useQueryClient()
  const [email, setEmail] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [ok, setOk] = useState<string | null>(null)

  const inviteMutation = useMutation({
    mutationFn: () => householdsApi.inviteMember(email.trim()),
    onSuccess: (invite) => {
      queryClient.invalidateQueries({ queryKey: ['sent-invites'] })
      setEmail('')
      setOk(`Convite enviado a ${invite.invited_user_name}.`)
    },
    onError: (err) => setError(errorMessage(err, 'Não foi possível enviar o convite.')),
  })

  return (
    <form
      className="flex flex-col gap-3"
      onSubmit={(e) => {
        e.preventDefault()
        setError(null)
        setOk(null)
        if (email.trim()) inviteMutation.mutate()
      }}
    >
      <div className="flex flex-col gap-1.5 sm:flex-row sm:items-end">
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="invite-email">Convidar por email</Label>
          <Input
            id="invite-email"
            type="email"
            autoComplete="off"
            placeholder="pessoa@exemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={!email.trim() || inviteMutation.isPending}>
          {inviteMutation.isPending ? 'A enviar...' : 'Enviar convite'}
        </Button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {ok && <p className="text-sm text-emerald-500">{ok}</p>}
    </form>
  )
}

function SentInvites() {
  const queryClient = useQueryClient()
  const { data: invites } = useQuery({
    queryKey: ['sent-invites'],
    queryFn: householdsApi.listSentInvites,
  })

  const cancelMutation = useMutation({
    mutationFn: householdsApi.cancelInvite,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sent-invites'] }),
  })

  if (!invites || invites.length === 0) return null

  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm font-medium">Convites pendentes</p>
      {invites.map((invite) => (
        <div
          key={invite.id}
          className="flex items-center justify-between gap-3 text-sm text-ink-muted"
        >
          <span>{invite.invited_user_email}</span>
          <Button
            size="sm"
            variant="ghost"
            disabled={cancelMutation.isPending}
            onClick={() => cancelMutation.mutate(invite.id)}
          >
            Cancelar
          </Button>
        </div>
      ))}
    </div>
  )
}

function HouseholdView({ household }: { household: Household }) {
  const reduceMotion = useReducedMotion()
  const queryClient = useQueryClient()
  const [confirmingLeave, setConfirmingLeave] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const leaveMutation = useMutation({
    mutationFn: householdsApi.leaveHousehold,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['household'] })
      queryClient.invalidateQueries({ queryKey: ['sent-invites'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
    onError: (err) => {
      setError(errorMessage(err, 'Não foi possível sair do agregado.'))
      setConfirmingLeave(false)
    },
  })

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{household.name}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            {household.members.map((member, index) => (
              <motion.div
                key={member.user_id}
                initial={reduceMotion ? false : { opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.06, ease: 'easeOut' }}
                className="flex items-center justify-between gap-3 rounded-lg border border-border p-3 text-sm"
              >
                <div>
                  <p className="font-medium text-ink">{member.name}</p>
                  <p className="text-ink-muted">{member.email}</p>
                </div>
                {member.is_creator && (
                  <span className="rounded-full bg-surface-hover px-2 py-0.5 text-xs text-ink-muted">
                    Criador
                  </span>
                )}
              </motion.div>
            ))}
          </div>

          <div className="flex flex-col gap-1">
            {confirmingLeave ? (
              <div className="flex items-center gap-2">
                <span className="text-sm text-ink-muted">Sair do agregado?</span>
                <Button
                  size="sm"
                  variant="destructive"
                  disabled={leaveMutation.isPending}
                  onClick={() => leaveMutation.mutate()}
                >
                  Confirmar
                </Button>
                <Button size="sm" variant="outline" onClick={() => setConfirmingLeave(false)}>
                  Cancelar
                </Button>
              </div>
            ) : (
              <div>
                <Button size="sm" variant="ghost" onClick={() => setConfirmingLeave(true)}>
                  Sair do agregado
                </Button>
              </div>
            )}
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Membros e convites</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-5">
          <InviteForm />
          <SentInvites />
        </CardContent>
      </Card>
    </>
  )
}

export function HouseholdPage() {
  const { data: household, isLoading, isError } = useQuery({
    queryKey: ['household'],
    queryFn: householdsApi.getMyHousehold,
  })
  const { data: receivedInvites } = useQuery({
    queryKey: ['received-invites'],
    queryFn: householdsApi.listReceivedInvites,
    enabled: !household && !isLoading,
  })

  return (
    <main className="mx-auto flex min-h-svh max-w-2xl flex-col gap-6 p-4 py-10">
      <PageHeader title="Agregado familiar" />

      {isLoading && <p className="text-sm text-ink-muted">A carregar...</p>}
      {isError && (
        <p className="text-sm text-red-600">Não foi possível carregar o agregado familiar.</p>
      )}

      {!isLoading && !isError && household && <HouseholdView household={household} />}
      {!isLoading && !isError && !household && (
        <>
          <ReceivedInvites invites={receivedInvites ?? []} />
          <CreateHouseholdCard />
        </>
      )}
    </main>
  )
}
