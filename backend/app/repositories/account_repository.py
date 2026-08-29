import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account, AccountType


def list_by_user(db: Session, user_id: uuid.UUID) -> list[Account]:
    return list(
        db.scalars(select(Account).where(Account.user_id == user_id).order_by(Account.created_at))
    )


def get_by_id_for_user(db: Session, account_id: uuid.UUID, user_id: uuid.UUID) -> Account | None:
    return db.scalar(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )


def create(
    db: Session, *, user_id: uuid.UUID, name: str, type: AccountType, initial_balance: Decimal
) -> Account:
    account = Account(
        user_id=user_id,
        name=name,
        type=type,
        initial_balance=initial_balance,
        current_balance=initial_balance,
    )
    db.add(account)
    db.flush()
    return account


def delete(db: Session, account: Account) -> None:
    db.delete(account)
