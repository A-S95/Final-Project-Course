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

test('exporta as transações para um ficheiro CSV', async ({ page }) => {
  await registerUser(page, { name: 'Duarte Export' })
  await createAccount(page, 'Conta Principal')
  await createCategory(page, 'Transportes', 'Despesa')
  await createTransaction(page, {
    account: 'Conta Principal',
    category: 'Transportes',
    amount: '9.90',
    description: 'Passe mensal',
  })

  await page.goto('/transacoes')
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Exportar CSV' }).click()
  const download = await downloadPromise

  expect(download.suggestedFilename()).toMatch(/^centisible-transacoes-\d{4}-\d{2}-\d{2}\.csv$/)
})
