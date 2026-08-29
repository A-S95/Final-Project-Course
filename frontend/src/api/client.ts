import type { AuthResponse } from '@/features/auth/types'
import { getAccessToken, setAccessToken } from './token-store'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

let inFlightRefresh: Promise<AuthResponse | null> | null = null

async function doRefresh(): Promise<AuthResponse | null> {
  const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })

  if (!response.ok) {
    setAccessToken(null)
    return null
  }

  const body = (await response.json()) as AuthResponse
  setAccessToken(body.access_token)
  return body
}

/**
 * Tenta renovar a sessão a partir do refresh token no cookie httpOnly.
 * Chamada tanto no arranque da app (para saber se já havia sessão) como
 * automaticamente quando um pedido falha com 401 por o access token ter
 * expirado (~15 min).
 *
 * O refresh token é rodado a cada uso (o backend revoga o antigo e emite um
 * novo) e trata reutilização de um token já rodado como possível roubo,
 * revogando toda a sessão. Sem este cache, duas chamadas concorrentes (ex:
 * StrictMode a invocar o useEffect duas vezes, ou vários pedidos em paralelo
 * a apanhar 401 ao mesmo tempo por o access token ter expirado) disparariam
 * dois pedidos de refresh com o mesmo cookie — o segundo usaria um token que
 * o primeiro já tinha rodado, acionando essa deteção e terminando a sessão à
 * força. Partilhar a mesma promise entre chamadas concorrentes garante que só
 * um pedido de refresh chega ao backend de cada vez.
 */
export function refreshSession(): Promise<AuthResponse | null> {
  if (!inFlightRefresh) {
    inFlightRefresh = doRefresh().finally(() => {
      inFlightRefresh = null
    })
  }
  return inFlightRefresh
}

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  body?: unknown
  /** Pedidos de auth (login/registo/refresh) não devem tentar renovar em 401. */
  skipAuthRetry?: boolean
}

/** Base comum a `request` (JSON) e aos dois helpers de ficheiros abaixo —
 * token + renovação em 401 num só sítio, para não duplicar essa dança. */
async function authedFetch(
  path: string,
  init: RequestInit,
  skipAuthRetry = false,
): Promise<Response> {
  const doFetch = (token: string | null) =>
    fetch(`${API_URL}${path}`, {
      ...init,
      credentials: 'include',
      headers: {
        ...init.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })

  let response = await doFetch(getAccessToken())

  if (response.status === 401 && !skipAuthRetry) {
    const refreshed = await refreshSession()
    if (refreshed) {
      response = await doFetch(refreshed.access_token)
    }
  }

  return response
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await authedFetch(
    path,
    {
      method: options.method ?? 'GET',
      headers: { 'Content-Type': 'application/json' },
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    },
    options.skipAuthRetry,
  )

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new ApiError(response.status, detail?.detail ?? `HTTP ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

/** Upload multipart — nunca definir Content-Type à mão, o browser trata do
 * boundary sozinho quando o body é um FormData. */
async function uploadFile<T>(path: string, file: File): Promise<T> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await authedFetch(path, { method: 'POST', body: formData })

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new ApiError(response.status, detail?.detail ?? `HTTP ${response.status}`)
  }
  return (await response.json()) as T
}

/** Ficheiros protegidos (ex: recibos) não podem ir num `<img src>` direto —
 * um pedido de imagem do browser não leva o header Authorization. Busca-se
 * como blob autenticado e cria-se um object URL local (ver `URL.revokeObjectURL`
 * do lado de quem chama, quando a imagem deixar de ser precisa). */
async function fetchBlob(path: string): Promise<Blob> {
  const response = await authedFetch(path, { method: 'GET' })
  if (!response.ok) {
    throw new ApiError(response.status, `HTTP ${response.status}`)
  }
  return response.blob()
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'POST', body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'PATCH', body }),
  delete: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'DELETE' }),
  uploadFile,
  fetchBlob,
}
