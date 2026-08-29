import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    AccountNotFoundError,
    CategoryNotFoundError,
    InvalidTransactionError,
    TransactionNotFoundError,
)
from app.db.session import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    type: TransactionType | None = None,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TransactionRead]:
    transactions = transaction_service.list_transactions(
        db,
        user_id=current_user.id,
        account_id=account_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
    )
    return [TransactionRead.model_validate(transaction) for transaction in transactions]


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    try:
        transaction = transaction_service.create_transaction(
            db,
            user_id=current_user.id,
            account_id=payload.account_id,
            destination_account_id=payload.destination_account_id,
            category_id=payload.category_id,
            type=payload.type,
            amount=payload.amount,
            description=payload.description,
            date=payload.date,
            is_shared=payload.is_shared,
        )
    except (AccountNotFoundError, CategoryNotFoundError) as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Conta ou categoria não encontrada."
        ) from exc
    except InvalidTransactionError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, exc.message) from exc

    db.commit()
    return TransactionRead.model_validate(transaction)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    try:
        transaction = transaction_service.update_transaction(
            db,
            user_id=current_user.id,
            transaction_id=transaction_id,
            account_id=payload.account_id,
            destination_account_id=payload.destination_account_id,
            category_id=payload.category_id,
            type=payload.type,
            amount=payload.amount,
            description=payload.description,
            date=payload.date,
            is_shared=payload.is_shared,
        )
    except TransactionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transação não encontrada.") from exc
    except (AccountNotFoundError, CategoryNotFoundError) as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Conta ou categoria não encontrada."
        ) from exc
    except InvalidTransactionError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, exc.message) from exc

    db.commit()
    return TransactionRead.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        transaction_service.delete_transaction(
            db, user_id=current_user.id, transaction_id=transaction_id
        )
    except TransactionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transação não encontrada.") from exc

    db.commit()
