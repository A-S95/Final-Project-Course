import { expect, test } from '@playwright/test'
import { registerUser, uniqueEmail } from './helpers'

test('regista uma conta nova e chega ao dashboard', async ({ page }) => {
  const { name } = await registerUser(page, { name: 'Ana Registo' })

  await expect(page).toHaveURL('/dashboard')
  // O painel cumprimenta só pelo primeiro nome (ver routes/dashboard.tsx).
  await expect(page.getByText(`Olá, ${name.split(' ')[0]}`)).toBeVisible()
})

test('a partir do login, pede uma ligação de recuperação de password', async ({ page }) => {
  await page.goto('/login')
  await page.getByRole('link', { name: 'Esqueceste-te da password?' }).click()
  await expect(page).toHaveURL('/recuperar-password')
  // Esperar a página assentar (transição do AnimatePresence) antes de preencher.
  await expect(page.getByRole('heading', { name: 'Recuperar password' })).toBeVisible()

  await page.getByLabel('Email').fill(uniqueEmail('reset'))
  await page.getByRole('button', { name: 'Enviar ligação' }).click()

  // Resposta genérica (não revela se a conta existe) + caminho de volta ao login.
  await expect(page.getByText(/Se existir uma conta com esse email/)).toBeVisible()
  await page.getByRole('link', { name: 'Voltar ao início de sessão' }).click()
  await expect(page).toHaveURL('/login')
})

test('a página de nova password sem token pede uma ligação nova', async ({ page }) => {
  await page.goto('/redefinir-password')
  await expect(page.getByText(/falta o código de recuperação/)).toBeVisible()
  await expect(page.getByRole('link', { name: 'Pedir nova ligação' })).toBeVisible()
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
