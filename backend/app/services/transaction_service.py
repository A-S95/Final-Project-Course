import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidTransactionError, TransactionNotFoundError
from app.models.account import Account
from app.models.category import CategoryType
from app.models.transaction import Transaction, TransactionType
from app.repositories import transaction_repository
from app.services import account_service, category_service


def _validate_combination(
    type: TransactionType,
    account_id: uuid.UUID,
    destination_account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
) -> None:
    if type == TransactionType.TRANSFER:
        if destination_account_id is None:
            raise InvalidTransactionError("Uma transferência exige uma conta de destino.")
        if destination_account_id == account_id:
            raise InvalidTransactionError(
                "A conta de destino tem de ser diferente da conta de origem."
            )
        if category_id is not None:
            raise InvalidTransactionError("Uma transferência não pode ter categoria.")
    else:
        if category_id is None:
            raise InvalidTransactionError("Escolhe uma categoria.")
        if destination_account_id is not None:
            raise InvalidTransactionError("Só uma transferência pode ter conta de destino.")


def _validate_category_type(type: TransactionType, category_type: CategoryType) -> None:
    if type.value != category_type.value:
        raise InvalidTransactionError(
            "O tipo da categoria tem de corresponder ao tipo da transação."
        )


def _apply_balance_effect(
    type: TransactionType,
    account: Account,
    destination: Account | None,
    amount: Decimal,
    *,
    sign: int,
) -> None:
    if type == TransactionType.INCOME:
        account.current_balance += sign * amount
    elif type == TransactionType.EXPENSE:
        account.current_balance -= sign * amount
    else:  # TRANSFER
        account.current_balance -= sign * amount
        if destination is not None:
            destination.current_balance += sign * amount


def list_transactions(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[Transaction]:
    return transaction_repository.list_by_user(
        db,
        user_id,
        account_id=account_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
    )


def get_transaction(db: Session, *, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction:
    transaction = transaction_repository.get_by_id_for_user(db, transaction_id, user_id)
    if transaction is None:
        raise TransactionNotFoundError
    return transaction


def create_transaction(
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
    _validate_combination(type, account_id, destination_account_id, category_id)

    account = account_service.get_account(db, user_id=user_id, account_id=account_id)
    destination = None
    if destination_account_id is not None:
        destination = account_service.get_account(
            db, user_id=user_id, account_id=destination_account_id
        )
    if category_id is not None:
        category = category_service.get_category(db, user_id=user_id, category_id=category_id)
        _validate_category_type(type, category.type)

    transaction = transaction_repository.create(
        db,
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
    _apply_balance_effect(type, account, destination, amount, sign=1)
    db.flush()
    return transaction


def update_transaction(
    db: Session,
    *,
    user_id: uuid.UUID,
    transaction_id: uuid.UUID,
    account_id: uuid.UUID,
    destination_account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
    type: TransactionType,
    amount: Decimal,
    description: str | None,
    date: date,
    is_shared: bool = False,
) -> Transaction:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)
    _validate_combination(type, account_id, destination_account_id, category_id)

    # Reverte o efeito da transação tal como estava antes de editar...
    old_account = account_service.get_account(
        db, user_id=user_id, account_id=transaction.account_id
    )
    old_destination = None
    if transaction.destination_account_id is not None:
        old_destination = account_service.get_account(
            db, user_id=user_id, account_id=transaction.destination_account_id
        )
    _apply_balance_effect(
        transaction.type, old_account, old_destination, transaction.amount, sign=-1
    )

    # ...e aplica o efeito da nova versão (contas podem ter mudado).
    new_account = account_service.get_account(db, user_id=user_id, account_id=account_id)
    new_destination = None
    if destination_account_id is not None:
        new_destination = account_service.get_account(
            db, user_id=user_id, account_id=destination_account_id
        )
    if category_id is not None:
        category = category_service.get_category(db, user_id=user_id, category_id=category_id)
        _validate_category_type(type, category.type)
    _apply_balance_effect(type, new_account, new_destination, amount, sign=1)

    transaction.account_id = account_id
    transaction.destination_account_id = destination_account_id
    transaction.category_id = category_id
    transaction.type = type
    transaction.amount = amount
    transaction.description = description
    transaction.date = date
    transaction.is_shared = is_shared

    db.flush()
    return transaction


def delete_transaction(db: Session, *, user_id: uuid.UUID, transaction_id: uuid.UUID) -> None:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)

    account = account_service.get_account(db, user_id=user_id, account_id=transaction.account_id)
    destination = None
    if transaction.destination_account_id is not None:
        destination = account_service.get_account(
            db, user_id=user_id, account_id=transaction.destination_account_id
        )
    _apply_balance_effect(transaction.type, account, destination, transaction.amount, sign=-1)

    transaction_repository.delete(db, transaction)
    db.flush()
