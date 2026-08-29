import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal


def list_by_user(db: Session, user_id: uuid.UUID) -> list[Goal]:
    return list(
        db.scalars(
            select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at)
        )
    )


def get_by_id_for_user(db: Session, goal_id: uuid.UUID, user_id: uuid.UUID) -> Goal | None:
    return db.scalar(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))


def create(db: Session, goal: Goal) -> Goal:
    db.add(goal)
    db.flush()
    return goal


def delete(db: Session, goal: Goal) -> None:
    db.delete(goal)
