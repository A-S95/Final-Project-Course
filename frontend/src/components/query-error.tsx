import { Button } from '@/components/ui/button'

// Falha ao carregar dados de uma query: mensagem + retry, em vez de um <p> vermelho
// sem saída. Usado em todas as páginas de lista para um tratamento de erro consistente.
export function QueryError({
  message = 'Não foi possível carregar os dados.',
  onRetry,
}: {
  message?: string
  onRetry: () => void
}) {
  return (
    <div className="flex flex-col items-start gap-2 rounded-xl border border-border bg-surface-raised p-4">
      <p className="text-sm text-red-600">{message}</p>
      <Button variant="outline" size="sm" onClick={onRetry}>
        Tentar novamente
      </Button>
    </div>
  )
}
