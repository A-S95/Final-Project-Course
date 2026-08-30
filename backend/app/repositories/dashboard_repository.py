import uuid
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from sqlalchemy import Row, String, case, cast, false, func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.user import User


def total_balance(db: Session, user_ids: Sequence[uuid.UUID]) -> Decimal:
    """Soma dos saldos atuais (estado 'agora') das contas dos utilizadores dados."""
    stmt = select(func.coalesce(func.sum(Account.current_balance), 0)).where(
        Account.user_id.in_(user_ids)
    )
    return db.scalar(stmt) or Decimal(0)


def sum_amount_by_type(
    db: Session,
    user_ids: Sequence[uuid.UUID],
    *,
    type: TransactionType,
    month_start: date,
    next_month_start: date,
) -> Decimal:
    """Total de transações de um tipo no intervalo [month_start, next_month_start[."""
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id.in_(user_ids),
        Transaction.type == type,
        Transaction.date >= month_start,
        Transaction.date < next_month_start,
    )
    return db.scalar(stmt) or Decimal(0)


def expenses_by_category(
    db: Session,
    user_ids: Sequence[uuid.UUID],
    *,
    month_start: date,
    next_month_start: date,
    group_by_name: bool = False,
) -> list[Row[tuple[uuid.UUID | str, str, str | None, Decimal, bool, str | None]]]:
    """Despesas do mês somadas por categoria, da maior para a menor. Só `EXPENSE` entra.

    `group_by_name` (vista de agregado, cada pessoa tem a sua própria categoria):
    despesas partilhadas (`is_shared=True`) fundem-se numa linha só, somando os
    valores (mesmo custo registado por mais que uma pessoa). Despesas pessoais
    homónimas (`is_shared=False`) ficam uma linha por pessoa (`owner_name`
    identifica de quem é) — são gastos independentes, não devem somar-se.
    """
    total = func.sum(Transaction.amount)

    if not group_by_name:
        # Vista individual: uma linha por categoria, `is_shared`/`owner_name` fixos.
        stmt = (
            select(
                Category.id,
                Category.name,
                Category.color,
                total,
                false(),
                func.cast(None, String),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id.in_(user_ids),
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= month_start,
                Transaction.date < next_month_start,
            )
            .group_by(Category.id, Category.name, Category.color)
            .order_by(total.desc())
        )
        return list(db.execute(stmt).all())

    # NULL funde todas as partilhadas num grupo só; user_id separa as pessoais por pessoa.
    person_key = case((Transaction.is_shared.is_(True), None), else_=Transaction.user_id)
    id_col = func.min(cast(Category.id, String))  # Postgres não tem min() nativo p/ UUID
    color_col = func.min(Category.color)
    owner_col = func.min(User.name)  # grupo pessoal só tem 1 utilizador; partilhada ignora isto
    stmt = (
        select(id_col, Category.name, color_col, total, Transaction.is_shared, owner_col)
        .join(Category, Transaction.category_id == Category.id)
        .join(User, Transaction.user_id == User.id)
        .where(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= month_start,
            Transaction.date < next_month_start,
        )
        .group_by(Category.name, Transaction.is_shared, person_key)
        .order_by(total.desc())
    )
    return list(db.execute(stmt).all())


def sum_shared_expenses(
    db: Session,
    user_ids: Sequence[uuid.UUID],
    *,
    month_start: date,
    next_month_start: date,
) -> Decimal:
    """Total de despesas marcadas como partilhadas (`Transaction.is_shared`)."""
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id.in_(user_ids),
        Transaction.type == TransactionType.EXPENSE,
        Transaction.is_shared.is_(True),
        Transaction.date >= month_start,
        Transaction.date < next_month_start,
    )
    return db.scalar(stmt) or Decimal(0)
