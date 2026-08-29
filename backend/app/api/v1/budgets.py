import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    BudgetAlreadyExistsError,
    BudgetCategoryInvalidError,
    BudgetNotFoundError,
    CategoryNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetRead])
def list_budgets(
    month: date | None = Query(
        default=None,
        description="Qualquer dia do mês (só ano/mês contam). Omitido = mês atual.",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BudgetRead]:
    return budget_service.list_budgets(
        db, user_id=current_user.id, period_month=month or date.today()
    )


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetRead:
    try:
        budget = budget_service.create_budget(
            db,
            user_id=current_user.id,
            category_id=payload.category_id,
            period_month=payload.period_month,
            amount=payload.amount,
        )
    except CategoryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada.") from exc
    except BudgetCategoryInvalidError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Só categorias de despesa podem ter orçamento.",
        ) from exc
    except BudgetAlreadyExistsError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Já existe um orçamento para esta categoria neste mês.",
        ) from exc

    db.commit()
    return budget


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: uuid.UUID,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetRead:
    try:
        budget = budget_service.update_budget(
            db, user_id=current_user.id, budget_id=budget_id, amount=payload.amount
        )
    except BudgetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Orçamento não encontrado.") from exc

    db.commit()
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        budget_service.delete_budget(db, user_id=current_user.id, budget_id=budget_id)
    except BudgetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Orçamento não encontrado.") from exc

    db.commit()
