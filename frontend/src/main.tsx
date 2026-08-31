import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ApiError } from '@/api/client'
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from './features/theme/theme-context.tsx'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Repetir falhas transitórias (rede, backend a acordar na Render), mas nunca
      // erros de autenticação/permissão/inexistência — esses não melhoram com retry.
      retry: (failureCount, error) => {
        if (error instanceof ApiError && [401, 403, 404].includes(error.status)) return false
        return failureCount < 2
      },
      staleTime: 30_000,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
)
