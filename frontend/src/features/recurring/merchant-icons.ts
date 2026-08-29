import {
  Clapperboard,
  CreditCard,
  Home,
  Music2,
  Repeat,
  ShoppingCart,
  Smartphone,
  type LucideIcon,
} from 'lucide-react'

// Reconhece marcas comuns em despesas recorrentes portuguesas pelo nome dado
// pelo utilizador (não há integração real com nenhuma marca — é só um ícone
// genérico da categoria, pintado com a cor mais associada a cada marca, para
// reconhecimento rápido no painel). Sem logótipos reais: evita reproduzir
// marcas registadas, e um ícone genérico + cor já chega para o objetivo aqui
// (ver "à primeira vista, de que empresa é isto").
type MerchantBadge = { icon: LucideIcon; color: string }

const MERCHANT_PATTERNS: Array<{ pattern: RegExp; badge: MerchantBadge }> = [
  { pattern: /netflix/i, badge: { icon: Clapperboard, color: '#E50914' } },
  { pattern: /spotify/i, badge: { icon: Music2, color: '#1DB954' } },
  { pattern: /vodafone/i, badge: { icon: Smartphone, color: '#E60000' } },
  { pattern: /\bnos\b/i, badge: { icon: Smartphone, color: '#E4032E' } },
  { pattern: /\bmeo\b/i, badge: { icon: Smartphone, color: '#00A950' } },
  { pattern: /revolut/i, badge: { icon: CreditCard, color: '#0666EB' } },
  { pattern: /universo/i, badge: { icon: CreditCard, color: '#E4004D' } },
  { pattern: /continente/i, badge: { icon: ShoppingCart, color: '#EE1C25' } },
  { pattern: /mercadona/i, badge: { icon: ShoppingCart, color: '#00A650' } },
  { pattern: /renda|aluguer/i, badge: { icon: Home, color: '#1f7a4c' } },
]

const DEFAULT_BADGE: MerchantBadge = { icon: Repeat, color: '#1f7a4c' }

export function merchantBadge(description: string): MerchantBadge {
  return MERCHANT_PATTERNS.find((entry) => entry.pattern.test(description))?.badge ?? DEFAULT_BADGE
}
