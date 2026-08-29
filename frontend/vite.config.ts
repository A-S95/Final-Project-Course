import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
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
