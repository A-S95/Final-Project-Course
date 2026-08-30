import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
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
    // Bind mounts do Docker Desktop no Windows não propagam eventos inotify
    // para dentro do container — sem polling, o Vite nunca deteta alterações
    // a ficheiros feitas no host e continua a servir a versão antiga em cache.
    watch: {
      usePolling: true,
    },
  },
})
