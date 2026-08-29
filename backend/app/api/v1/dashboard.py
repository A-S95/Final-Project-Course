from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardScope, DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary)
def get_dashboard(
    month: date | None = Query(
        default=None,
        description="Qualquer dia do mês a resumir (só ano/mês contam). Omitido = mês atual.",
    ),
    scope: DashboardScope = Query(
        default=DashboardScope.INDIVIDUAL,
        description="'individual' (só os meus dados) ou 'household' (soma do agregado familiar).",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummary:
    return dashboard_service.get_summary(
        db, user_id=current_user.id, month=month, scope=scope
    )
