import uuid
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
    db: Session, *, user_id: uuid.UUID, name: str, type: AccountType, initial_balance: Decimal
) -> Account:
    return account_repository.create(
        db, user_id=user_id, name=name, type=type, initial_balance=initial_balance
    )


def update_account(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID,
    name: str | None,
    type: AccountType | None,
    initial_balance: Decimal | None,
) -> Account:
    account = get_account(db, user_id=user_id, account_id=account_id)

    if name is not None:
        account.name = name
    if type is not None:
        account.type = type
    if initial_balance is not None and initial_balance != account.initial_balance:
        # `current_balance` já pode divergir do `initial_balance` por causa de
        # transações lançadas entretanto (Fase 5) — em vez de o sobrescrever,
        # aplica-se só a diferença, preservando o efeito dessas transações.
        delta = initial_balance - account.initial_balance
        account.current_balance += delta
        account.initial_balance = initial_balance

    db.flush()
    return account


def delete_account(db: Session, *, user_id: uuid.UUID, account_id: uuid.UUID) -> None:
    account = get_account(db, user_id=user_id, account_id=account_id)
    account_repository.delete(db, account)
    try:
        db.flush()
    except IntegrityError as exc:
        # FK ON DELETE RESTRICT de `transactions` (Fase 5) ou `recurring_expenses`
        # (Fase 9) — a conta está a ser usada. `rollback()` desfaz só até ao savepoint
        # mais recente (ver tests/conftest.py), deixando a sessão utilizável.
        db.rollback()
        raise AccountInUseError from exc
