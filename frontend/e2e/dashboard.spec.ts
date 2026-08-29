import { type Page, expect, test } from '@playwright/test'
import { createAccount, createCategory, createTransaction, registerUser } from './helpers'

function statValue(page: Page, label: string) {
  return page.getByText(label, { exact: true }).locator('..').locator('.text-2xl')
}

test('dashboard carrega com dados após criar transações', async ({ page }) => {
  await registerUser(page, { name: 'Eduardo Dashboard' })

  await createAccount(page, 'Conta Ordenado')
  await createCategory(page, 'Salário', 'Receita')
  await createCategory(page, 'Renda', 'Despesa')

  await createTransaction(page, {
    type: 'Receita',
    account: 'Conta Ordenado',
    category: 'Salário',
    amount: '1200',
    description: 'Ordenado de agosto',
  })
  await createTransaction(page, {
    type: 'Despesa',
    account: 'Conta Ordenado',
    category: 'Renda',
    amount: '400',
    description: 'Renda de casa',
  })

  await page.goto('/dashboard')

  await expect(statValue(page, 'Saldo global')).toHaveText(/800,00\s*€/)
  await expect(statValue(page, 'Receitas do mês')).toHaveText(/1\.?200,00\s*€/)
  await expect(statValue(page, 'Despesas do mês')).toHaveText(/400,00\s*€/)
})
