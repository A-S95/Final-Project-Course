import { expect, test } from '@playwright/test'
import { registerUser, uniqueEmail } from './helpers'

test('regista uma conta nova e chega ao dashboard', async ({ page }) => {
  const { name } = await registerUser(page, { name: 'Ana Registo' })

  await expect(page).toHaveURL('/dashboard')
  // O painel cumprimenta só pelo primeiro nome (ver routes/dashboard.tsx).
  await expect(page.getByText(`Olá, ${name.split(' ')[0]}`)).toBeVisible()
})

test('permite iniciar sessão com uma conta existente', async ({ page }) => {
  const email = uniqueEmail('login')
  const password = 'Password123'
  await registerUser(page, { email, password, name: 'Bruno Login' })

  await page.getByRole('button', { name: 'Terminar sessão' }).click()
  await expect(page).toHaveURL('/login')

  await page.locator('#email').fill(email)
  await page.locator('#password').fill(password)
  await page.getByRole('button', { name: 'Entrar' }).click()

  await expect(page).toHaveURL('/dashboard')
  await expect(page.getByText('Olá, Bruno')).toBeVisible()
})
