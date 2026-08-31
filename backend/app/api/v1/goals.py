import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.goal import GoalContribution, GoalCreate, GoalRead, GoalUpdate
from app.services import goal_service

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalRead])
def list_goals(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[GoalRead]:
    return goal_service.list_goals(db, user_id=current_user.id)


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalRead:
    goal = goal_service.create_goal(
        db,
        user_id=current_user.id,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
    )
    db.commit()
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: uuid.UUID,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalRead:
    goal = goal_service.update_goal(
        db,
        user_id=current_user.id,
        goal_id=goal_id,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
    )
    db.commit()
    return goal


@router.post("/{goal_id}/contributions", response_model=GoalRead)
def contribute_to_goal(
    goal_id: uuid.UUID,
    payload: GoalContribution,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalRead:
    goal = goal_service.contribute(
        db, user_id=current_user.id, goal_id=goal_id, amount=payload.amount
    )
    db.commit()
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    goal_service.delete_goal(db, user_id=current_user.id, goal_id=goal_id)
    db.commit()
