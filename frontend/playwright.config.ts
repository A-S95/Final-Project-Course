import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    // As animações (Framer Motion) respeitam prefers-reduced-motion — sem
    // isto, testes que leem um valor final logo após a ação (ex: a barra de
    // progresso de um orçamento) corriam risco de apanhar um frame a meio da
    // animação, em vez do resultado final.
    reducedMotion: 'reduce',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
