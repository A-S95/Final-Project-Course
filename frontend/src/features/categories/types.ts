export const CATEGORY_TYPES = ['INCOME', 'EXPENSE'] as const
export type CategoryType = (typeof CATEGORY_TYPES)[number]

export const CATEGORY_TYPE_LABELS: Record<CategoryType, string> = {
  INCOME: 'Receita',
  EXPENSE: 'Despesa',
}

export type Category = {
  id: string
  name: string
  type: CategoryType
  icon: string | null
  color: string | null
  created_at: string
  updated_at: string
}

export type CategoryInput = {
  name: string
  type: CategoryType
  icon?: string | null
  color?: string | null
}

// Paleta curada para o seletor de cor — as mesmas cores servem de fallback
// no gráfico do dashboard (`routes/dashboard.tsx`) para categorias sem cor
// definida, por isso escolher uma daqui garante sempre bom contraste em
// ambos os temas.
export const CATEGORY_COLOR_PALETTE = [
  '#6552f5',
  '#0ea5e9',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
] as const

// Conjunto pequeno e deliberadamente genérico — cobre as categorias mais
// comuns de uma app de finanças pessoais sem precisar de uma biblioteca de
// ícones (o campo `icon` é só texto livre no modelo).
export const CATEGORY_ICON_OPTIONS = [
  '🍔',
  '🛒',
  '🚗',
  '🚌',
  '🏠',
  '⚡',
  '📱',
  '🎬',
  '🎮',
  '☕',
  '🍺',
  '👕',
  '💊',
  '🏋️',
  '🐶',
  '✈️',
  '🎓',
  '🎁',
  '🔧',
  '🧾',
  '💰',
  '💼',
  '📈',
  '💳',
] as const
