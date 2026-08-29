import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category, CategoryType


def list_by_user(db: Session, user_id: uuid.UUID) -> list[Category]:
    return list(
        db.scalars(
            select(Category).where(Category.user_id == user_id).order_by(Category.created_at)
        )
    )


def get_by_id_for_user(db: Session, category_id: uuid.UUID, user_id: uuid.UUID) -> Category | None:
    return db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )


def get_by_name_for_user(db: Session, name: str, user_id: uuid.UUID) -> Category | None:
    return db.scalar(select(Category).where(Category.user_id == user_id, Category.name == name))


def create(
    db: Session,
    *,
    user_id: uuid.UUID,
    name: str,
    type: CategoryType,
    icon: str | None,
    color: str | None,
) -> Category:
    category = Category(user_id=user_id, name=name, type=type, icon=icon, color=color)
    db.add(category)
    db.flush()
    return category


def delete(db: Session, category: Category) -> None:
    db.delete(category)
