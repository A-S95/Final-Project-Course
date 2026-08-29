import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import AccountInUseError, AccountNotFoundError
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
    try:
        account = account_service.update_account(
            db,
            user_id=current_user.id,
            account_id=account_id,
            name=payload.name,
            type=payload.type,
            initial_balance=payload.initial_balance,
        )
    except AccountNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta não encontrada.") from exc

    db.commit()
    return AccountRead.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        account_service.delete_account(db, user_id=current_user.id, account_id=account_id)
    except AccountNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conta não encontrada.") from exc
    except AccountInUseError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Esta conta está a ser usada (transações ou despesas recorrentes) e não pode ser "
            "eliminada.",
        ) from exc

    db.commit()
