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
) -> list[Row[tuple[uuid.UUID | str, str, str | None, Decimal, bool, str | None]]]:
    """Despesas do mês somadas por categoria, ordenadas da maior para a menor.

    Só `EXPENSE` entra — receitas e transferências não são "gastos por categoria".
    As duas últimas colunas (`is_shared`, `owner_name`) só se destinam a
    desambiguar a vista de agregado (ver abaixo) — na vista individual vêm
    sempre `False`/`None` e o serviço ignora-as.

    `group_by_name`: na vista de agregado, cada pessoa tem a sua própria categoria
    "Alimentação" (categorias são sempre de um só utilizador). A forma correta de
    juntar isto depende de a despesa ser partilhada ou não:
    - **Partilhada** (`is_shared=True`): é o mesmo custo, só registado por mais que
      uma pessoa (ex: os dois marcam a mesma renda) — funde-se sempre numa única
      linha, somando os valores, ou a despesa apareceria a dobrar.
    - **Pessoal** (`is_shared=False`): são despesas independentes que só por
      coincidência têm o mesmo nome de categoria (ex: cada um paga a sua própria
      renda a senhorios diferentes, ou têm ambos uma categoria "Lazer" para gastos
      que nada têm a ver um com o outro) — juntar os valores numa só linha somaria
      duas despesas não relacionadas como se fossem uma, o que é enganador. Ficam
      uma linha por pessoa, com `owner_name` a identificar de quem é cada uma.
    """
    total = func.sum(Transaction.amount)

    if not group_by_name:
        # Vista individual: `is_shared` não interessa aqui (só desambigua entre
        # pessoas diferentes na vista de agregado) — uma só linha por categoria,
        # como sempre, com valores constantes nas duas colunas extra.
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

    # `person_key`: `NULL` para despesas partilhadas (todas as pessoas caem no
    # mesmo grupo, sejam quem forem — é isso que as funde), o `user_id` para
    # despesas pessoais (cada pessoa fica no seu próprio grupo, mesmo com o
    # mesmo nome de categoria que outra).
    person_key = case((Transaction.is_shared.is_(True), None), else_=Transaction.user_id)
    # Postgres não tem min() nativo para UUID — passa por texto e volta a
    # UUID (o Pydantic aceita a string na resposta na mesma).
    id_col = func.min(cast(Category.id, String))
    color_col = func.min(Category.color)
    # Dentro de um grupo pessoal há sempre um só utilizador, por isso `min` só
    # escolhe entre valores iguais; num grupo partilhado o nome não se usa
    # (o serviço ignora-o quando `is_shared` é verdadeiro).
    owner_col = func.min(User.name)
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
