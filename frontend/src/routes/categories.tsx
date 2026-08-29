import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { ApiError } from '@/api/client'
import { PageHeader } from '@/components/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import * as categoriesApi from '@/features/categories/api'
import { categorySchema, type CategoryFormValues } from '@/features/categories/schemas'
import {
  CATEGORY_COLOR_PALETTE,
  CATEGORY_ICON_OPTIONS,
  CATEGORY_TYPE_LABELS,
  CATEGORY_TYPES,
  type Category,
} from '@/features/categories/types'

function ColorPicker({
  value,
  onChange,
}: {
  value: string | null
  onChange: (color: string) => void
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {CATEGORY_COLOR_PALETTE.map((color) => (
        <button
          key={color}
          type="button"
          aria-label={`Cor ${color}`}
          aria-pressed={value === color}
          onClick={() => onChange(color)}
          className={`h-7 w-7 rounded-full transition-transform ${value === color ? 'ring-2 ring-ink ring-offset-2 ring-offset-surface' : 'hover:scale-110'}`}
          style={{ backgroundColor: color }}
        />
      ))}
    </div>
  )
}

function IconPicker({
  value,
  onChange,
}: {
  value: string | null
  onChange: (icon: string | null) => void
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      <button
        type="button"
        aria-label="Sem ícone"
        aria-pressed={!value}
        onClick={() => onChange(null)}
        className={`flex h-8 w-8 items-center justify-center rounded-md border text-sm text-ink-muted ${!value ? 'border-accent bg-accent/10' : 'border-border hover:bg-surface-hover'}`}
      >
        —
      </button>
      {CATEGORY_ICON_OPTIONS.map((icon) => (
        <button
          key={icon}
          type="button"
          aria-label={`Ícone ${icon}`}
          aria-pressed={value === icon}
          onClick={() => onChange(icon)}
          className={`flex h-8 w-8 items-center justify-center rounded-md border text-base ${value === icon ? 'border-accent bg-accent/10' : 'border-border hover:bg-surface-hover'}`}
        >
          {icon}
        </button>
      ))}
    </div>
  )
}

function CategoryForm({
  defaultValues,
  onSubmit,
  onCancel,
  submitLabel,
}: {
  defaultValues: CategoryFormValues
  onSubmit: (values: CategoryFormValues) => Promise<void>
  onCancel?: () => void
  submitLabel: string
}) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<CategoryFormValues>({ resolver: zodResolver(categorySchema), defaultValues })
  const icon = watch('icon')
  const color = watch('color')

  const submit = async (values: CategoryFormValues) => {
    setFormError(null)
    try {
      await onSubmit(values)
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Não foi possível guardar a categoria.')
    }
  }

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="name">Nome</Label>
          <Input id="name" autoComplete="off" {...register('name')} />
          {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
        </div>
        <div className="flex flex-1 flex-col gap-1.5">
          <Label htmlFor="type">Tipo</Label>
          <Select id="type" {...register('type')}>
            {CATEGORY_TYPES.map((type) => (
              <option key={type} value={type}>
                {CATEGORY_TYPE_LABELS[type]}
              </option>
            ))}
          </Select>
        </div>
      </div>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        <div className="flex flex-1 flex-col gap-1.5">
          <Label>Cor</Label>
          <ColorPicker value={color} onChange={(value) => setValue('color', value)} />
        </div>
        <div className="flex flex-[2] flex-col gap-1.5">
          <Label>Ícone</Label>
          <IconPicker value={icon} onChange={(value) => setValue('icon', value)} />
        </div>
      </div>
      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'A guardar...' : submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
        )}
      </div>
      {formError && <p className="text-sm text-red-600">{formError}</p>}
    </form>
  )
}

function CategoryRow({
  category,
  index,
  otherCategoriesOfSameType,
}: {
  category: Category
  index: number
  otherCategoriesOfSameType: Category[]
}) {
  const reduceMotion = useReducedMotion()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [inUse, setInUse] = useState(false)
  const [reassignTo, setReassignTo] = useState('')
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: (values: CategoryFormValues) => categoriesApi.updateCategory(category.id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setIsEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (reassignToCategoryId?: string) =>
      categoriesApi.deleteCategory(category.id, reassignToCategoryId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] }),
    onError: (err) => {
      if (err instanceof ApiError && err.status === 409) {
        // Categoria tem transações associadas — oferece reatribuí-las em vez
        // de só mostrar o erro (ver `category_service.delete_category`).
        setInUse(true)
        return
      }
      setDeleteError(
        err instanceof ApiError ? err.message : 'Não foi possível eliminar a categoria.',
      )
      setConfirmingDelete(false)
    },
  })

  if (isEditing) {
    return (
      <div className="border-b border-border p-4 last:border-0">
        <CategoryForm
          defaultValues={{
            name: category.name,
            type: category.type,
            icon: category.icon,
            color: category.color,
          }}
          submitLabel="Guardar"
          onCancel={() => setIsEditing(false)}
          onSubmit={(values) => updateMutation.mutateAsync(values).then(() => undefined)}
        />
      </div>
    )
  }

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04, ease: 'easeOut' }}
      className="flex flex-wrap items-center justify-between gap-3 border-b border-border p-4 last:border-0"
    >
      <div className="flex items-center gap-3">
        <span
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm"
          style={{ backgroundColor: `${category.color ?? '#94a3b8'}26` }}
        >
          {category.icon ?? (
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: category.color ?? '#94a3b8' }}
            />
          )}
        </span>
        <div>
          <p className="font-medium text-ink">{category.name}</p>
          <p className="text-sm text-ink-muted">{CATEGORY_TYPE_LABELS[category.type]}</p>
          {deleteError && <p className="text-sm text-red-600">{deleteError}</p>}
        </div>
      </div>
      {inUse ? (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-ink-muted">
            Em uso. Mover transações para outra categoria e eliminar:
          </span>
          <Select
            value={reassignTo}
            onChange={(e) => setReassignTo(e.target.value)}
            className="w-auto"
          >
            <option value="">Escolhe uma categoria</option>
            {otherCategoriesOfSameType.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
          <Button
            variant="destructive"
            size="sm"
            disabled={!reassignTo || deleteMutation.isPending}
            onClick={() => deleteMutation.mutate(reassignTo)}
          >
            Mover e eliminar
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setInUse(false)
              setConfirmingDelete(false)
            }}
          >
            Cancelar
          </Button>
        </div>
      ) : confirmingDelete ? (
        <div className="flex items-center gap-2">
          <span className="text-sm text-ink-muted">Eliminar?</span>
          <Button
            variant="destructive"
            size="sm"
            disabled={deleteMutation.isPending}
            onClick={() => deleteMutation.mutate(undefined)}
          >
            Confirmar
          </Button>
          <Button variant="outline" size="sm" onClick={() => setConfirmingDelete(false)}>
            Cancelar
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
            Editar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setDeleteError(null)
              setConfirmingDelete(true)
            }}
          >
            Eliminar
          </Button>
        </div>
      )}
    </motion.div>
  )
}

export function CategoriesPage() {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)

  const { data: categories, isLoading, isError } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.listCategories,
  })

  const createMutation = useMutation({
    mutationFn: categoriesApi.createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setIsCreating(false)
    },
  })

  return (
    <main className="mx-auto flex min-h-svh max-w-2xl flex-col gap-6 p-4 py-10">
      <PageHeader title="Categorias" />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Nova categoria</CardTitle>
        </CardHeader>
        <CardContent>
          {isCreating ? (
            <CategoryForm
              defaultValues={{ name: '', type: 'EXPENSE', icon: null, color: CATEGORY_COLOR_PALETTE[0] }}
              submitLabel="Criar categoria"
              onCancel={() => setIsCreating(false)}
              onSubmit={(values) => createMutation.mutateAsync(values).then(() => undefined)}
            />
          ) : (
            <Button onClick={() => setIsCreating(true)}>Adicionar categoria</Button>
          )}
        </CardContent>
      </Card>

      <Card>
        {isLoading && <p className="p-6 text-sm text-ink-muted">A carregar...</p>}
        {isError && (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar as categorias.</p>
        )}
        {categories && categories.length === 0 && (
          <p className="p-6 text-sm text-ink-muted">
            Ainda não tens nenhuma categoria.
          </p>
        )}
        {categories?.map((category, index) => (
          <CategoryRow
            key={category.id}
            category={category}
            index={index}
            otherCategoriesOfSameType={categories.filter(
              (c) => c.id !== category.id && c.type === category.type,
            )}
          />
        ))}
      </Card>
    </main>
  )
}
