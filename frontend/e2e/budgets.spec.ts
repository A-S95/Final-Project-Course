import { expect, test } from '@playwright/test'
import { createAccount, createCategory, createTransaction, registerUser } from './helpers'

test('cria um orçamento e mostra a barra de progresso com o gasto', async ({ page }) => {
  await registerUser(page, { name: 'Diana Orçamentos' })

  await createAccount(page, 'Conta Corrente')
  await createCategory(page, 'Lazer', 'Despesa')
  await createTransaction(page, {
    account: 'Conta Corrente',
    category: 'Lazer',
    amount: '30',
    description: 'Cinema',
  })

  await page.goto('/orcamentos')
  await page.locator('#budget-category').selectOption({ label: 'Lazer' })
  await page.locator('#budget-amount').fill('100')
  await page.getByRole('button', { name: 'Adicionar' }).click()

  const row = page.getByText('Lazer').locator('..').locator('..')
  await expect(row.getByText(/30,00\s*€\s*\/\s*100,00\s*€\s*·\s*30%/)).toBeVisible()

  const progressFill = page.locator('.bg-emerald-500').first()
  await expect(progressFill).toBeVisible()
  await expect(progressFill).toHaveAttribute('style', /width:\s*30%/)
})
