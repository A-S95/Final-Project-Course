import math
import uuid
from datetime import date
from decimal import ROUND_UP, Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import GoalNotFoundError, InvalidGoalContributionError
from app.models.goal import Goal
from app.repositories import goal_repository
from app.schemas.goal import GoalRead

_CENTS = Decimal("0.01")


def _months_until(deadline: date, today: date) -> int:
    """Meses (aproximados) até ao prazo: dias / 30, arredondado para cima, mínimo 1."""
    return max(1, math.ceil((deadline - today).days / 30))


def _to_read(goal: Goal, *, today: date) -> GoalRead:
    # `current_amount`/`target_amount` são normalizados a 2 casas — quando vêm de um
    # default Pydantic (`Decimal("0")`) e não de um round-trip à BD, ainda não têm
    # as casas decimais fixas.
    target = goal.target_amount.quantize(_CENTS)
    current = goal.current_amount.quantize(_CENTS)
    remaining = max(target - current, Decimal(0)).quantize(_CENTS)
    is_achieved = current >= target
    progress = float(current / target * 100) if target else 0.0

    months_until: int | None = None
    required_monthly: Decimal | None = None
    deadline_passed = False
    if goal.deadline is not None and not is_achieved:
        if goal.deadline < today:
            deadline_passed = True
        else:
            months_until = _months_until(goal.deadline, today)
            required_monthly = (remaining / months_until).quantize(_CENTS, rounding=ROUND_UP)

    return GoalRead(
        id=goal.id,
        name=goal.name,
        target_amount=target,
        current_amount=current,
        deadline=goal.deadline,
        remaining=remaining,
        progress_percentage=round(progress, 1),
        is_achieved=is_achieved,
        deadline_passed=deadline_passed,
        months_until_deadline=months_until,
        required_monthly_contribution=required_monthly,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


def get_goal(db: Session, *, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
    goal = goal_repository.get_by_id_for_user(db, goal_id, user_id)
    if goal is None:
        raise GoalNotFoundError
    return goal


def list_goals(db: Session, *, user_id: uuid.UUID) -> list[GoalRead]:
    today = date.today()
    return [_to_read(goal, today=today) for goal in goal_repository.list_by_user(db, user_id)]


def create_goal(
    db: Session,
    *,
    user_id: uuid.UUID,
    name: str,
    target_amount: Decimal,
    current_amount: Decimal,
    deadline: date | None,
) -> GoalRead:
    goal = Goal(
        user_id=user_id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        deadline=deadline,
    )
    goal_repository.create(db, goal)
    return _to_read(goal, today=date.today())


def update_goal(
    db: Session,
    *,
    user_id: uuid.UUID,
    goal_id: uuid.UUID,
    name: str | None,
    target_amount: Decimal | None,
    current_amount: Decimal | None,
    deadline: date | None,
    deadline_set: bool,
) -> GoalRead:
    goal = get_goal(db, user_id=user_id, goal_id=goal_id)

    if name is not None:
        goal.name = name
    if target_amount is not None:
        goal.target_amount = target_amount
    if current_amount is not None:
        goal.current_amount = current_amount
    if deadline_set:
        # `deadline` pode ser uma data (definir/alterar) ou None (limpar o prazo).
        goal.deadline = deadline

    db.flush()
    return _to_read(goal, today=date.today())


def contribute(
    db: Session, *, user_id: uuid.UUID, goal_id: uuid.UUID, amount: Decimal
) -> GoalRead:
    goal = get_goal(db, user_id=user_id, goal_id=goal_id)
    new_amount = goal.current_amount + amount
    if new_amount < 0:
        raise InvalidGoalContributionError
    goal.current_amount = new_amount
    db.flush()
    return _to_read(goal, today=date.today())


def delete_goal(db: Session, *, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
    goal = get_goal(db, user_id=user_id, goal_id=goal_id)
    goal_repository.delete(db, goal)
    db.flush()
