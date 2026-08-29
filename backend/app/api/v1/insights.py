from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.insight import Insight
from app.services import insights_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", response_model=list[Insight])
def list_insights(
    month: date | None = Query(
        default=None, description="Qualquer dia do mês. Omitido = mês atual."
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Insight]:
    return insights_service.get_insights(db, user_id=current_user.id, month=month)
