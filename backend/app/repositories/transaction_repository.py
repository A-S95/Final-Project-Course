import uuid
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.user import User


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


def find_shared_expense_duplicate(
    db: Session,
    *,
    member_user_ids: Sequence[uuid.UUID],
    exclude_user_id: uuid.UUID,
    category_name: str,
    amount: Decimal,
    month_start: date,
    next_month_start: date,
) -> str | None:
    """Procura uma despesa partilhada já lançada por OUTRO membro do agregado com a
    mesma categoria (por nome — cada pessoa tem a sua) e o mesmo valor, no mesmo mês.

    Devolve o nome do dono da despesa encontrada (para a mensagem de aviso) ou
    `None` se não houver nenhuma. Serve de guarda contra o casal lançar a mesma
    renda/conta da casa duas vezes (ver `transaction_service._check_shared_duplicate`).
    """
    stmt = (
        select(User.name)
        .select_from(Transaction)
        .join(Category, Transaction.category_id == Category.id)
        .join(User, Transaction.user_id == User.id)
        .where(
            Transaction.user_id.in_(member_user_ids),
            Transaction.user_id != exclude_user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.is_shared.is_(True),
            Transaction.amount == amount,
            Transaction.date >= month_start,
            Transaction.date < next_month_start,
            func.lower(Category.name) == category_name.lower(),
        )
        .limit(1)
    )
    return db.scalar(stmt)


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
