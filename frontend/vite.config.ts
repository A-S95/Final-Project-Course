import { readFileSync } from 'node:fs'
import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// Fonte única dos cabeçalhos de segurança: o vercel.json (produção). Aqui só se
// derivam versões para o servidor local, para as violações de CSP (fontes,
// imagens, estilos, connect) aparecerem já em `npm run dev`/`preview` e não só
// depois do deploy.
function securityHeaders(mode: 'dev' | 'preview'): Record<string, string> {
  const vercel = JSON.parse(
    readFileSync(new URL('./vercel.json', import.meta.url), 'utf-8'),
  ) as { headers: { headers: { key: string; value: string }[] }[] }
  const headers = Object.fromEntries(
    vercel.headers[0].headers.map((h) => [h.key, h.value]),
  ) as Record<string, string>

  let csp = headers['Content-Security-Policy']
  // Em localhost a API é http://localhost:8000 e o HMR do Vite usa websockets.
  csp = csp.replace(
    "connect-src 'self' https://centisible.onrender.com",
    "connect-src 'self' http://localhost:8000 ws://localhost:*",
  )
  // O dev server do Vite injeta scripts inline (preâmbulo do React Refresh) e usa
  // eval — coisas que não existem no build de produção. O `preview` serve o build
  // real, por isso mantém o script-src 'self' estrito.
  if (mode === 'dev') {
    csp = csp.replace("script-src 'self'", "script-src 'self' 'unsafe-inline' 'unsafe-eval'")
  }
  headers['Content-Security-Policy'] = csp
  // HSTS forçaria o browser a tentar https em localhost.
  delete headers['Strict-Transport-Security']
  return headers
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      // Ficheiro externo em vez do <script> inline por omissão — mantém a CSP
      // do frontend com script-src 'self' (ver frontend/vercel.json).
      injectRegister: 'script',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'CentiSible — Gestão Financeira',
        short_name: 'CentiSible',
        description: 'Gestão financeira pessoal e familiar: contas, orçamentos, objetivos e agregado.',
        theme_color: '#1f7a4c',
        background_color: '#f7f9f7',
        lang: 'pt-PT',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: 'maskable-icon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // Só faz precache dos assets do build (JS/CSS/HTML/ícones). Os
        // pedidos à API (backend noutra origem) nunca são intercetados por
        // omissão — mas a regra abaixo torna isso explícito: dados
        // financeiros nunca vêm de cache, só da rede.
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
            handler: 'NetworkOnly',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    headers: securityHeaders('dev'),
    // Bind mounts do Docker Desktop no Windows não propagam eventos inotify
    // para dentro do container — sem polling, o Vite nunca deteta alterações
    // a ficheiros feitas no host e continua a servir a versão antiga em cache.
    watch: {
      usePolling: true,
    },
  },
  preview: {
    headers: securityHeaders('preview'),
  },
})
