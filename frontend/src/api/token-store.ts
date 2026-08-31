// Só em memória, nunca localStorage (mitiga XSS, ver ARCHITECTURE.md secção 8).
// Módulo à parte para o cliente HTTP e o AuthContext partilharem a mesma fonte.

let accessToken: string | null = null

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}

// O cliente HTTP avisa aqui quando o refresh token é mesmo rejeitado (sessão
// terminada), para o AuthContext poder reagir e mandar para o login — em vez de
// deixar a app presa a mostrar erros de "não autenticado" numa página protegida.
let sessionExpiredHandler: (() => void) | null = null

export function setSessionExpiredHandler(handler: (() => void) | null): void {
  sessionExpiredHandler = handler
}

export function notifySessionExpired(): void {
  sessionExpiredHandler?.()
}
