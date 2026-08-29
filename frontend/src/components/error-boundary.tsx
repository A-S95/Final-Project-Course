import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'

type Props = { children: ReactNode }
type State = { error: Error | null }

// Componente de classe de propósito — é a única forma que o React oferece de
// apanhar erros de render de componentes descendentes (não há equivalente em
// hooks). Sem isto, um erro inesperado em qualquer página deixava a SPA
// inteira em branco, sem qualquer forma de recuperar sem um refresh manual.
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Erro não tratado numa página:', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-canvas p-4 text-center">
          <h1 className="font-display text-xl font-semibold text-ink">Ocorreu um erro inesperado</h1>
          <p className="max-w-sm text-sm text-ink-muted">
            A página encontrou um problema e não pode continuar. Tenta recarregar — se o
            problema persistir, os teus dados não foram afetados.
          </p>
          <Button onClick={() => window.location.assign('/')}>Voltar ao início</Button>
        </main>
      )
    }
    return this.props.children
  }
}
