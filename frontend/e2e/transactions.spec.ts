import { expect, test } from '@playwright/test'
import { createAccount, createCategory, createTransaction, registerUser } from './helpers'

test('cria conta, categoria e transação e reflete o saldo', async ({ page }) => {
  await registerUser(page, { name: 'Carla Transações' })

  await createAccount(page, 'Conta Principal')
  await createCategory(page, 'Alimentação', 'Despesa')

  await createTransaction(page, {
    account: 'Conta Principal',
    category: 'Alimentação',
    amount: '45.50',
    description: 'Compras no supermercado',
  })

  await expect(page.getByText('Compras no supermercado')).toBeVisible()
  await expect(page.getByText(/-45,50\s*€/)).toBeVisible()

  await page.goto('/contas')
  await expect(page.getByText(/-45,50\s*€/)).toBeVisible()
})
