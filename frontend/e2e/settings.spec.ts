import { expect, test } from '@playwright/test'
import { registerUser } from './helpers'

test('edita o nome e a moeda em Definições e o dashboard reflete a mudança', async ({ page }) => {
  await registerUser(page, { name: 'Fernanda Definições' })

  await page.goto('/definicoes')
  await page.locator('#name').fill('Fernanda Editada')
  await page.locator('#currency').selectOption({ label: 'Dólar americano (USD)' })
  await page.getByRole('button', { name: 'Guardar' }).click()

  await expect(page.getByText('Definições guardadas.')).toBeVisible()

  await page.goto('/dashboard')
  await expect(page.getByText('Olá, Fernanda Editada')).toBeVisible()

  await page.reload()
  await expect(page.getByText('Olá, Fernanda Editada')).toBeVisible()
})
