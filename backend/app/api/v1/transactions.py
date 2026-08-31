import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
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


@router.get("/export")
def export_transactions(
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    type: TransactionType | None = None,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    content = transaction_service.export_transactions_csv(
        db,
        user_id=current_user.id,
        account_id=account_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
    )
    filename = f"centisible-transacoes-{date.today().isoformat()}.csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
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
    db.commit()
    return TransactionRead.model_validate(transaction)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
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
    db.commit()
    return TransactionRead.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    transaction_service.delete_transaction(
        db, user_id=current_user.id, transaction_id=transaction_id
    )
    db.commit()


@router.post("/{transaction_id}/receipt", response_model=TransactionRead)
async def upload_receipt(
    transaction_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    content = await file.read()
    transaction = transaction_service.save_receipt(
        db,
        user_id=current_user.id,
        transaction_id=transaction_id,
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )
    db.commit()
    return TransactionRead.model_validate(transaction)


@router.get("/{transaction_id}/receipt")
def download_receipt(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    content, content_type = transaction_service.get_receipt(
        db, user_id=current_user.id, transaction_id=transaction_id
    )
    return Response(content=content, media_type=content_type)


@router.delete("/{transaction_id}/receipt", response_model=TransactionRead)
def remove_receipt(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionRead:
    transaction = transaction_service.delete_receipt(
        db, user_id=current_user.id, transaction_id=transaction_id
    )
    db.commit()
    return TransactionRead.model_validate(transaction)
