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

// Mesma paleta serve de fallback no gráfico do dashboard para categorias sem cor.
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

// Genérico de propósito: `icon` é texto livre no modelo, não precisa de biblioteca.
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
