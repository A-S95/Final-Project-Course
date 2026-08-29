import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    CategoryInUseError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    InvalidCategoryReassignError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[CategoryRead]:
    categories = category_service.list_categories(db, user_id=current_user.id)
    return [CategoryRead.model_validate(category) for category in categories]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryRead:
    try:
        category = category_service.create_category(
            db,
            user_id=current_user.id,
            name=payload.name,
            type=payload.type,
            icon=payload.icon,
            color=payload.color,
        )
    except CategoryNameAlreadyExistsError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Já existe uma categoria com este nome."
        ) from exc

    db.commit()
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryRead:
    try:
        category = category_service.update_category(
            db,
            user_id=current_user.id,
            category_id=category_id,
            name=payload.name,
            type=payload.type,
            icon=payload.icon,
            color=payload.color,
        )
    except CategoryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada.") from exc
    except CategoryNameAlreadyExistsError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Já existe uma categoria com este nome."
        ) from exc

    db.commit()
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: uuid.UUID,
    reassign_to_category_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        category_service.delete_category(
            db,
            user_id=current_user.id,
            category_id=category_id,
            reassign_to_category_id=reassign_to_category_id,
        )
    except CategoryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada.") from exc
    except InvalidCategoryReassignError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, exc.message) from exc
    except CategoryInUseError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Esta categoria está a ser usada (transações, orçamentos ou despesas recorrentes) e "
            "não pode ser eliminada.",
        ) from exc

    db.commit()
