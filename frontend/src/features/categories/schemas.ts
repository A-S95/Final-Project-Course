import { z } from 'zod'
import { CATEGORY_TYPES } from './types'

export const categorySchema = z.object({
  name: z.string().min(1, 'Introduz um nome'),
  type: z.enum(CATEGORY_TYPES),
  icon: z.string().nullable(),
  color: z.string().nullable(),
})
export type CategoryFormValues = z.infer<typeof categorySchema>
