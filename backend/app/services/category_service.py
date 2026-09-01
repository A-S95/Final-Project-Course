import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CategoryInUseError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    InvalidCategoryReassignError,
)
from app.models.category import Category, CategoryType
from app.repositories import category_repository, transaction_repository

# Criadas automaticamente ao registar uma conta — sem isto o novo utilizador
# fica com o painel e os formulários de transação/orçamento vazios e sem forma
# óbvia de arrancar. São categorias normais: pode editá-las ou apagá-las.
DEFAULT_CATEGORIES: tuple[tuple[str, CategoryType, str, str], ...] = (
    ("Alimentação", CategoryType.EXPENSE, "🍔", "#ef4444"),
    ("Supermercado", CategoryType.EXPENSE, "🛒", "#f59e0b"),
    ("Transportes", CategoryType.EXPENSE, "🚗", "#0ea5e9"),
    ("Habitação", CategoryType.EXPENSE, "🏠", "#6552f5"),
    ("Contas e serviços", CategoryType.EXPENSE, "⚡", "#14b8a6"),
    ("Saúde", CategoryType.EXPENSE, "💊", "#10b981"),
    ("Lazer", CategoryType.EXPENSE, "🎬", "#ec4899"),
    ("Compras", CategoryType.EXPENSE, "👕", "#8b5cf6"),
    ("Educação", CategoryType.EXPENSE, "🎓", "#8b5cf6"),
    ("Salário", CategoryType.INCOME, "💰", "#10b981"),
    ("Outros rendimentos", CategoryType.INCOME, "📈", "#0ea5e9"),
)


def list_categories(db: Session, *, user_id: uuid.UUID) -> list[Category]:
    return category_repository.list_by_user(db, user_id)


def create_default_categories(db: Session, *, user_id: uuid.UUID) -> list[Category]:
    return [
        category_repository.create(
            db, user_id=user_id, name=name, type=type, icon=icon, color=color
        )
        for name, type, icon, color in DEFAULT_CATEGORIES
    ]


def get_category(db: Session, *, user_id: uuid.UUID, category_id: uuid.UUID) -> Category:
    category = category_repository.get_by_id_for_user(db, category_id, user_id)
    if category is None:
        raise CategoryNotFoundError
    return category


def create_category(
    db: Session,
    *,
    user_id: uuid.UUID,
    name: str,
    type: CategoryType,
    icon: str | None,
    color: str | None,
) -> Category:
    if category_repository.get_by_name_for_user(db, name, user_id) is not None:
        raise CategoryNameAlreadyExistsError
    return category_repository.create(
        db, user_id=user_id, name=name, type=type, icon=icon, color=color
    )


def update_category(
    db: Session,
    *,
    user_id: uuid.UUID,
    category_id: uuid.UUID,
    name: str,
    type: CategoryType,
    icon: str | None,
    color: str | None,
) -> Category:
    category = get_category(db, user_id=user_id, category_id=category_id)

    if name != category.name:
        existing = category_repository.get_by_name_for_user(db, name, user_id)
        if existing is not None and existing.id != category.id:
            raise CategoryNameAlreadyExistsError

    category.name = name
    category.type = type
    category.icon = icon
    category.color = color

    db.flush()
    return category


def delete_category(
    db: Session,
    *,
    user_id: uuid.UUID,
    category_id: uuid.UUID,
    reassign_to_category_id: uuid.UUID | None = None,
) -> None:
    category = get_category(db, user_id=user_id, category_id=category_id)

    if reassign_to_category_id is not None:
        if reassign_to_category_id == category_id:
            raise InvalidCategoryReassignError(
                "A categoria de destino tem de ser diferente da categoria a eliminar."
            )
        target = category_repository.get_by_id_for_user(db, reassign_to_category_id, user_id)
        if target is None:
            raise InvalidCategoryReassignError("Categoria de destino não encontrada.")
        if target.type != category.type:
            raise InvalidCategoryReassignError(
                "A categoria de destino tem de ser do mesmo tipo (receita/despesa)."
            )
        # Só transações são reatribuídas; orçamentos/recorrentes continuam a
        # bloquear a eliminação (colisões no UNIQUE de orçamentos, caso secundário).
        transaction_repository.reassign_category(
            db, user_id=user_id, from_category_id=category_id, to_category_id=target.id
        )

    category_repository.delete(db, category)
    try:
        db.flush()
    except IntegrityError as exc:
        # FK RESTRICT de transactions/budgets/recurring_expenses: categoria em uso.
        db.rollback()
        raise CategoryInUseError from exc
