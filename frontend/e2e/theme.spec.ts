import { expect, test } from '@playwright/test'
import { registerUser } from './helpers'

test('alterna entre tema claro e escuro, e a escolha sobrevive a um reload', async ({ page }) => {
  await registerUser(page, { name: 'Tema Teste' })

  // Sem escolha manual, segue o sistema — não afirmamos qual, só que muda ao clicar.
  const before = await page.evaluate(() => document.documentElement.getAttribute('data-theme'))

  await page.getByRole('button', { name: /Ativar tema/ }).click()
  const after = await page.evaluate(() => document.documentElement.getAttribute('data-theme'))
  expect(after).not.toBe(before)
  expect(['light', 'dark']).toContain(after)

  await page.reload()
  const afterReload = await page.evaluate(() =>
    document.documentElement.getAttribute('data-theme'),
  )
  expect(afterReload).toBe(after)
})
