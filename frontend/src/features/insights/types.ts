export type InsightSeverity = 'warning' | 'info' | 'positive'

export type Insight = {
  rule: string
  severity: InsightSeverity
  title: string
  detail: string
}
