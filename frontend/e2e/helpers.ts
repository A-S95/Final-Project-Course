import { type Page, expect } from '@playwright/test'

// example.com é o domínio reservado pela IANA para documentação/testes — passa
// no email-validator do backend, ao contrário de TLDs como .test ou .local,
// que são rejeitados por serem "special-use or reserved" (RFC 2606).
export function uniqueEmail(prefix: string) {
  return `${prefix}.${Date.now()}.${Math.floor(Math.random() * 100_000)}@example.com`
}

export async function registerUser(
  page: Page,
  opts?: { name?: string; email?: string; password?: string },
) {
  const email = opts?.email ?? uniqueEmail('user')
  const password = opts?.password ?? 'Password123'
  const name = opts?.name ?? 'Utilizador E2E'

  await page.goto('/registar')
  await page.locator('#name').fill(name)
  await page.locator('#email').fill(email)
  await page.locator('#password').fill(password)
  await page.getByRole('button', { name: 'Criar conta' }).click()
  // Espera pelo URL do dashboard, não pelo texto "CentiSible" — o título da
  // própria página de registo também contém a marca e faz o getByRole por
  // nome corresponder demasiado cedo.
  await expect(page).toHaveURL('/dashboard')

  return { email, password, name }
}

export async function createAccount(page: Page, name: string) {
  await page.goto('/contas')
  await page.getByRole('button', { name: 'Adicionar conta' }).click()
  await page.locator('#name').fill(name)
  await page.getByRole('button', { name: 'Criar conta' }).click()
  await expect(page.getByText(name).first()).toBeVisible()
}

export async function createCategory(
  page: Page,
  name: string,
  type: 'Despesa' | 'Receita' = 'Despesa',
) {
  await page.goto('/categorias')
  await page.getByRole('button', { name: 'Adicionar categoria' }).click()
  await page.locator('#name').fill(name)
  await page.locator('#type').selectOption({ label: type })
  await page.getByRole('button', { name: 'Criar categoria' }).click()
  await expect(page.getByText(name).first()).toBeVisible()
}

export async function createTransaction(
  page: Page,
  opts: {
    type?: 'Receita' | 'Despesa'
    account: string
    category: string
    amount: string
    date?: string
    description?: string
  },
) {
  await page.goto('/transacoes')
  await page.getByRole('button', { name: 'Adicionar transação' }).click()
  if (opts.type) {
    await page.locator('#type').selectOption({ label: opts.type })
  }
  await page.locator('#account_id').selectOption({ label: opts.account })
  await page.locator('#category_id').selectOption({ label: opts.category })
  await page.locator('#amount').fill(opts.amount)
  if (opts.date) {
    await page.locator('#date').fill(opts.date)
  }
  if (opts.description) {
    await page.locator('#description').fill(opts.description)
  }
  await page.getByRole('button', { name: 'Criar transação' }).click()
  await expect(page.getByRole('button', { name: 'Adicionar transação' })).toBeVisible()
}
