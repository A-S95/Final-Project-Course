import { expect, test } from '@playwright/test'
import { registerUser } from './helpers'

test('mostra a landing page a um visitante e leva ao registo/login', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: /dinheiro/i })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Criar conta grátis' }).first()).toHaveAttribute(
    'href',
    '/registar',
  )
  await expect(page.getByRole('link', { name: 'Já tenho conta' })).toHaveAttribute(
    'href',
    '/login',
  )
})

test('redireciona um utilizador autenticado da landing para o dashboard', async ({ page }) => {
  await registerUser(page, { name: 'Landing Redirect' })

  await page.goto('/')

  await expect(page).toHaveURL('/dashboard')
})
