// Só em memória, nunca localStorage (mitiga XSS, ver ARCHITECTURE.md secção 8).
// Módulo à parte para o cliente HTTP e o AuthContext partilharem a mesma fonte.

let accessToken: string | null = null

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}
