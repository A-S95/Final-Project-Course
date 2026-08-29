import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType


def list_by_user(
    db: Session,
    user_id: uuid.UUID,
    *,
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[Transaction]:
    stmt = select(Transaction).where(Transaction.user_id == user_id)
    if account_id is not None:
        # Uma conta pode ser origem ou destino (transferência) — ambas contam
        # como "movimentos desta conta" do ponto de vista do extrato.
        stmt = stmt.where(
            or_(
                Transaction.account_id == account_id,
                Transaction.destination_account_id == account_id,
            )
        )
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if type is not None:
        stmt = stmt.where(Transaction.type == type)
    if date_from is not None:
        stmt = stmt.where(Transaction.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Transaction.date <= date_to)

    stmt = stmt.order_by(Transaction.date.desc(), Transaction.created_at.desc())
    return list(db.scalars(stmt))


def get_by_id_for_user(
    db: Session, transaction_id: uuid.UUID, user_id: uuid.UUID
) -> Transaction | None:
    return db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user_id)
    )


def create(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID,
    destination_account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
    type: TransactionType,
    amount: Decimal,
    description: str | None,
    date: date,
    is_shared: bool = False,
) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        account_id=account_id,
        destination_account_id=destination_account_id,
        category_id=category_id,
        type=type,
        amount=amount,
        description=description,
        date=date,
        is_shared=is_shared,
    )
    db.add(transaction)
    db.flush()
    return transaction


def delete(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)


def reassign_category(
    db: Session, *, user_id: uuid.UUID, from_category_id: uuid.UUID, to_category_id: uuid.UUID
) -> int:
    """Move todas as transações de `from_category_id` para `to_category_id` — usado
    ao eliminar uma categoria com transações associadas (ver `category_service`)."""
    result = db.execute(
        update(Transaction)
        .where(Transaction.user_id == user_id, Transaction.category_id == from_category_id)
        .values(category_id=to_category_id)
    )
    db.flush()
    return result.rowcount
