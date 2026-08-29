import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recurring_expense import RecurringExpense


def list_by_user(db: Session, user_id: uuid.UUID) -> list[RecurringExpense]:
    return list(
        db.scalars(
            select(RecurringExpense)
            .where(RecurringExpense.user_id == user_id)
            .order_by(RecurringExpense.next_occurrence)
        )
    )


def get_by_id_for_user(
    db: Session, recurring_id: uuid.UUID, user_id: uuid.UUID
) -> RecurringExpense | None:
    return db.scalar(
        select(RecurringExpense).where(
            RecurringExpense.id == recurring_id, RecurringExpense.user_id == user_id
        )
    )


def list_due_for_user(
    db: Session, user_id: uuid.UUID, on_date: date
) -> list[RecurringExpense]:
    """Recorrências ativas do utilizador com uma ocorrência por gerar até `on_date`."""
    return list(
        db.scalars(
            select(RecurringExpense)
            .where(
                RecurringExpense.user_id == user_id,
                RecurringExpense.active.is_(True),
                RecurringExpense.next_occurrence <= on_date,
            )
            .order_by(RecurringExpense.next_occurrence)
        )
    )


def create(db: Session, recurring: RecurringExpense) -> RecurringExpense:
    db.add(recurring)
    db.flush()
    return recurring


def delete(db: Session, recurring: RecurringExpense) -> None:
    db.delete(recurring)
