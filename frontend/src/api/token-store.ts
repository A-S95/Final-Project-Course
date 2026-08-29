// O access token vive só em memória (nunca localStorage/sessionStorage — mitiga
// roubo via XSS, ver ARCHITECTURE.md secção 8). Fica num módulo à parte do React
// para o cliente HTTP (fora da árvore de componentes) e o AuthContext (dentro
// dela) partilharem a mesma fonte de verdade, através de useSyncExternalStore.

type Listener = () => void

let accessToken: string | null = null
const listeners = new Set<Listener>()

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
  for (const listener of listeners) listener()
}

export function subscribeAccessToken(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}
