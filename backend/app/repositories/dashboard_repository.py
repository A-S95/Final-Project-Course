import uuid
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from sqlalchemy import Row, String, cast, func, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType


def total_balance(db: Session, user_ids: Sequence[uuid.UUID]) -> Decimal:
    """Soma dos saldos atuais das contas dos utilizadores dados (estado 'agora').

    `user_ids` tem um único elemento na vista individual e vários na vista de
    agregado familiar — a query é a mesma, só muda o `IN (...)`.
    """
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
) -> list[Row[tuple[uuid.UUID | str, str, str | None, Decimal]]]:
    """Despesas do mês somadas por categoria, ordenadas da maior para a menor.

    Só `EXPENSE` entra — receitas e transferências não são "gastos por categoria".

    `group_by_name`: na vista de agregado, cada pessoa tem a sua própria categoria
    "Alimentação" (categorias são sempre de um só utilizador) — sem isto, apareceriam
    como duas linhas separadas em vez de uma só despesa combinada do casal. Agrupar
    por nome funde-as; `category_id`/`color` tornam-se arbitrários nesse caso (o de
    valor mais baixo), já que já não representam uma única categoria real.
    """
    total = func.sum(Transaction.amount)
    group_cols = (
        (Category.name,) if group_by_name else (Category.id, Category.name, Category.color)
    )
    # Postgres não tem min() nativo para UUID — passa por texto e volta a
    # UUID (o Pydantic aceita a string na resposta na mesma).
    id_col = func.min(cast(Category.id, String)) if group_by_name else Category.id
    color_col = func.min(Category.color) if group_by_name else Category.color
    stmt = (
        select(id_col, Category.name, color_col, total)
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= month_start,
            Transaction.date < next_month_start,
        )
        .group_by(*group_cols)
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
