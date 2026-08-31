import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AccountInUseError, AccountNotFoundError
from app.models.account import Account, AccountType
from app.repositories import account_repository


def list_accounts(db: Session, *, user_id: uuid.UUID) -> list[Account]:
    return account_repository.list_by_user(db, user_id)


def get_account(db: Session, *, user_id: uuid.UUID, account_id: uuid.UUID) -> Account:
    account = account_repository.get_by_id_for_user(db, account_id, user_id)
    if account is None:
        raise AccountNotFoundError
    return account


def create_account(
    db: Session,
    *,
    user_id: uuid.UUID,
    name: str,
    type: AccountType,
    initial_balance: Decimal,
    card_expiration_date: date | None = None,
    card_plafond: Decimal | None = None,
) -> Account:
    return account_repository.create(
        db,
        user_id=user_id,
        name=name,
        type=type,
        initial_balance=initial_balance,
        card_expiration_date=card_expiration_date,
        card_plafond=card_plafond,
    )


def update_account(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID,
    name: str,
    type: AccountType,
    initial_balance: Decimal,
    card_expiration_date: date | None,
    card_plafond: Decimal | None,
) -> Account:
    account = get_account(db, user_id=user_id, account_id=account_id)

    account.name = name
    account.type = type
    if initial_balance != account.initial_balance:
        # Aplica só a diferença, para preservar o efeito de transações já lançadas.
        account.current_balance += initial_balance - account.initial_balance
        account.initial_balance = initial_balance
    account.card_expiration_date = card_expiration_date
    account.card_plafond = card_plafond

    db.flush()
    return account


def delete_account(db: Session, *, user_id: uuid.UUID, account_id: uuid.UUID) -> None:
    account = get_account(db, user_id=user_id, account_id=account_id)
    account_repository.delete(db, account)
    try:
        db.flush()
    except IntegrityError as exc:
        # FK RESTRICT de transactions/recurring_expenses: conta em uso.
        db.rollback()
        raise AccountInUseError from exc
