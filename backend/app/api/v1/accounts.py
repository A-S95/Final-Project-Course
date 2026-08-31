import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountRead])
def list_accounts(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[AccountRead]:
    accounts = account_service.list_accounts(db, user_id=current_user.id)
    return [AccountRead.model_validate(account) for account in accounts]


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    account = account_service.create_account(
        db,
        user_id=current_user.id,
        name=payload.name,
        type=payload.type,
        initial_balance=payload.initial_balance,
        card_expiration_date=payload.card_expiration_date,
        card_plafond=payload.card_plafond,
    )
    db.commit()
    return AccountRead.model_validate(account)


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    account_id: uuid.UUID,
    payload: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    # PATCH mas com o formulário completo — a UI reenvia sempre todos os campos
    # (ver schemas/account.py e o docstring de TransactionUpdate).
    account = account_service.update_account(
        db,
        user_id=current_user.id,
        account_id=account_id,
        name=payload.name,
        type=payload.type,
        initial_balance=payload.initial_balance,
        card_expiration_date=payload.card_expiration_date,
        card_plafond=payload.card_plafond,
    )
    db.commit()
    return AccountRead.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    account_service.delete_account(db, user_id=current_user.id, account_id=account_id)
    db.commit()
