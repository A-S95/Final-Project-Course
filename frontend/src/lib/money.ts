// Formatação e validação de valores monetários, partilhadas por todas as páginas.

export function formatMoney(value: string | number, currency: string): string {
  return new Intl.NumberFormat('pt-PT', { style: 'currency', currency }).format(Number(value))
}

// Texto livre de um input de valor: "123" ou "123.45" (ponto, até 2 casas
// decimais). Evita a vírgula flutuante de <input type="number"> — ver os forms.
export const AMOUNT_RE = /^\d+(\.\d{1,2})?$/
