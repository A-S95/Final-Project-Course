import { useContext } from 'react'
import { ThemeContext } from './theme-context'

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme tem de ser usado dentro de <ThemeProvider>')
  return ctx
}
