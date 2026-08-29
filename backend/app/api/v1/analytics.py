from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import MonthComparison, MonthlyTrend
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/monthly-comparison", response_model=MonthComparison)
def monthly_comparison(
    month: date | None = Query(
        default=None, description="Qualquer dia do mês. Omitido = mês atual."
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MonthComparison:
    return analytics_service.get_comparison(db, user_id=current_user.id, month=month)


@router.get("/monthly-trend", response_model=MonthlyTrend)
def monthly_trend(
    months: int = Query(default=6, ge=2, le=24),
    month: date | None = Query(
        default=None, description="Último mês da série. Omitido = mês atual."
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MonthlyTrend:
    return analytics_service.get_trend(
        db, user_id=current_user.id, months=months, month=month
    )
