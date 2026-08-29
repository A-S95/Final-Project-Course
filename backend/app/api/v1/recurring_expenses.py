import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    AccountNotFoundError,
    CategoryNotFoundError,
    RecurringExpenseCategoryInvalidError,
    RecurringExpenseNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.recurring_expense import (
    RecurringExpenseCreate,
    RecurringExpenseRead,
    RecurringExpenseUpdate,
    RecurringRunResult,
)
from app.services import recurring_expense_service

router = APIRouter(prefix="/recurring-expenses", tags=["recurring-expenses"])

_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Despesa recorrente não encontrada.")
_REF_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Conta ou categoria não encontrada.")
_CATEGORY_INVALID = HTTPException(
    status.HTTP_422_UNPROCESSABLE_CONTENT,
    "Uma despesa recorrente tem de usar uma categoria de despesa.",
)


@router.get("", response_model=list[RecurringExpenseRead])
def list_recurring_expenses(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[RecurringExpenseRead]:
    return recurring_expense_service.list_recurring(db, user_id=current_user.id)


@router.post("", response_model=RecurringExpenseRead, status_code=status.HTTP_201_CREATED)
def create_recurring_expense(
    payload: RecurringExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringExpenseRead:
    try:
        recurring = recurring_expense_service.create_recurring(
            db,
            user_id=current_user.id,
            account_id=payload.account_id,
            category_id=payload.category_id,
            description=payload.description,
            amount=payload.amount,
            frequency=payload.frequency,
            next_occurrence=payload.next_occurrence,
            active=payload.active,
        )
    except (AccountNotFoundError, CategoryNotFoundError) as exc:
        raise _REF_NOT_FOUND from exc
    except RecurringExpenseCategoryInvalidError as exc:
        raise _CATEGORY_INVALID from exc

    db.commit()
    return recurring


@router.post("/generate", response_model=RecurringRunResult)
def generate_recurring_transactions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RecurringRunResult:
    result = recurring_expense_service.generate_due(db, user_id=current_user.id)
    db.commit()
    return result


@router.patch("/{recurring_id}", response_model=RecurringExpenseRead)
def update_recurring_expense(
    recurring_id: uuid.UUID,
    payload: RecurringExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecurringExpenseRead:
    try:
        recurring = recurring_expense_service.update_recurring(
            db,
            user_id=current_user.id,
            recurring_id=recurring_id,
            account_id=payload.account_id,
            category_id=payload.category_id,
            description=payload.description,
            amount=payload.amount,
            frequency=payload.frequency,
            next_occurrence=payload.next_occurrence,
            active=payload.active,
        )
    except RecurringExpenseNotFoundError as exc:
        raise _NOT_FOUND from exc
    except (AccountNotFoundError, CategoryNotFoundError) as exc:
        raise _REF_NOT_FOUND from exc
    except RecurringExpenseCategoryInvalidError as exc:
        raise _CATEGORY_INVALID from exc

    db.commit()
    return recurring


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_expense(
    recurring_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        recurring_expense_service.delete_recurring(
            db, user_id=current_user.id, recurring_id=recurring_id
        )
    except RecurringExpenseNotFoundError as exc:
        raise _NOT_FOUND from exc

    db.commit()
