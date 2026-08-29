import calendar
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardScope
from app.schemas.insight import Insight, InsightSeverity
from app.services import (
    account_service,
    analytics_service,
    budget_service,
    dashboard_service,
    goal_service,
)

_SEVERITY_ORDER = {
    InsightSeverity.WARNING: 0,
    InsightSeverity.INFO: 1,
    InsightSeverity.POSITIVE: 2,
}

# Janela de aviso antes da validade de um cartão — nem tão cedo que o
# alerta perca urgência, nem tão tarde que não dê tempo de reagir.
_CARD_EXPIRATION_WARNING_DAYS = 30


def _eur(value: Decimal) -> str:
    """1400 -> "1 400,00 €" (estilo pt-PT, sem depender de locale do SO)."""
    formatted = f"{value:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} €"


def _month_elapsed_fraction(month_start: date, today: date) -> float:
    """Fração do mês já decorrida: 0.0 se o mês é futuro, 1.0 se já passou, e a
    proporção de dias se é o mês atual."""
    if (month_start.year, month_start.month) == (today.year, today.month):
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        return today.day / days_in_month
    if (month_start.year, month_start.month) < (today.year, today.month):
        return 1.0
    return 0.0


def get_insights(
    db: Session,
    *,
    user_id: uuid.UUID,
    month: date | None = None,
    today: date | None = None,
) -> list[Insight]:
    # `today` é injetável para os testes conseguirem exercitar as regras que
    # dependem de "quanto do mês já passou" (o ritmo de gasto de um orçamento).
    today = today or date.today()
    month_start = (month or today).replace(day=1)
    is_current_month = (month_start.year, month_start.month) == (today.year, today.month)
    elapsed = _month_elapsed_fraction(month_start, today)

    summary = dashboard_service.get_summary(
        db, user_id=user_id, month=month_start, scope=DashboardScope.INDIVIDUAL
    )
    comparison = analytics_service.get_comparison(db, user_id=user_id, month=month_start)
    budgets = budget_service.list_budgets(db, user_id=user_id, period_month=month_start)
    goals = goal_service.list_goals(db, user_id=user_id) if is_current_month else []
    # Saldo/validade são estado "agora", não do mês em navegação — só fazem
    # sentido ao ver o mês atual (mesmo critério usado para os objetivos).
    accounts = account_service.list_accounts(db, user_id=user_id) if is_current_month else []

    insights: list[Insight] = []

    # --- orçamentos ---
    for budget in budgets:
        pct = round(budget.percentage)
        if budget.percentage > 100:
            insights.append(
                Insight(
                    rule="budget_exceeded",
                    severity=InsightSeverity.WARNING,
                    title=f"Orçamento de {budget.category_name} ultrapassado",
                    detail=f"Gastaste {_eur(budget.spent)} de {_eur(budget.amount)} ({pct}%).",
                )
            )
        elif budget.percentage >= 80:
            insights.append(
                Insight(
                    rule="budget_near_limit",
                    severity=InsightSeverity.WARNING,
                    title=f"Orçamento de {budget.category_name} quase no limite",
                    detail=f"{_eur(budget.spent)} de {_eur(budget.amount)} usados ({pct}%).",
                )
            )
        elif 0 < elapsed < 1 and budget.spent > 0 and budget.percentage > elapsed * 100 + 20:
            insights.append(
                Insight(
                    rule="budget_pace",
                    severity=InsightSeverity.WARNING,
                    title=f"Ritmo alto no orçamento de {budget.category_name}",
                    detail=(
                        f"Já usaste {pct}% do orçamento com o mês "
                        f"{round(elapsed * 100)}% decorrido."
                    ),
                )
            )

    # --- variação de despesa face ao mês anterior ---
    prev_expenses = comparison.previous.total_expenses
    current_expenses = comparison.current.total_expenses
    change = current_expenses - prev_expenses
    change_pct = comparison.expenses_change_pct
    if change_pct is not None:
        if change_pct >= 20 and change >= 50:
            insights.append(
                Insight(
                    rule="expenses_up",
                    severity=InsightSeverity.WARNING,
                    title=f"Despesas {round(change_pct)}% acima do mês anterior",
                    detail=(
                        f"{_eur(current_expenses)} este mês vs {_eur(prev_expenses)} "
                        f"no mês anterior."
                    ),
                )
            )
        elif change_pct <= -15 and -change >= 50:
            insights.append(
                Insight(
                    rule="expenses_down",
                    severity=InsightSeverity.POSITIVE,
                    title=f"Despesas {round(abs(change_pct))}% abaixo do mês anterior",
                    detail=(
                        f"{_eur(current_expenses)} este mês vs {_eur(prev_expenses)} "
                        f"no mês anterior."
                    ),
                )
            )

    # --- poupança do mês ---
    if summary.net < 0:
        insights.append(
            Insight(
                rule="negative_net",
                severity=InsightSeverity.WARNING,
                title="Gastaste mais do que ganhaste este mês",
                detail=f"A poupança do mês está em {_eur(summary.net)}.",
            )
        )
    elif summary.savings_rate is not None and summary.savings_rate >= 20:
        insights.append(
            Insight(
                rule="healthy_savings",
                severity=InsightSeverity.POSITIVE,
                title="Boa taxa de poupança",
                detail=f"Poupaste {summary.savings_rate}% das receitas este mês.",
            )
        )

    # --- objetivos (só na vista do mês atual) ---
    for goal in goals:
        if goal.deadline_passed:
            insights.append(
                Insight(
                    rule="goal_deadline_passed",
                    severity=InsightSeverity.WARNING,
                    title=f'O prazo do objetivo "{goal.name}" já passou',
                    detail=f"Faltavam {_eur(goal.remaining)} para o alvo.",
                )
            )
        elif (
            goal.required_monthly_contribution is not None
            and goal.required_monthly_contribution > max(summary.net, Decimal(0))
        ):
            insights.append(
                Insight(
                    rule="goal_off_pace",
                    severity=InsightSeverity.WARNING,
                    title=f'O objetivo "{goal.name}" pode não chegar a tempo',
                    detail=(
                        f"Precisas de {_eur(goal.required_monthly_contribution)}/mês e este "
                        f"mês poupaste {_eur(summary.net)}."
                    ),
                )
            )

    # --- cartões: validade e plafond (só na vista do mês atual) ---
    for account in accounts:
        if account.card_expiration_date is not None:
            days_left = (account.card_expiration_date - today).days
            if days_left < 0:
                insights.append(
                    Insight(
                        rule="card_expired",
                        severity=InsightSeverity.WARNING,
                        title=f"O cartão {account.name} já expirou",
                        detail=(
                            f"Validade terminou a {account.card_expiration_date:%d/%m/%Y} — "
                            "renova para continuar a usá-lo."
                        ),
                    )
                )
            elif days_left <= _CARD_EXPIRATION_WARNING_DAYS:
                insights.append(
                    Insight(
                        rule="card_expiring_soon",
                        severity=InsightSeverity.WARNING,
                        title=f"O cartão {account.name} expira em breve",
                        detail=(
                            f"Válido até {account.card_expiration_date:%d/%m/%Y} "
                            f"({days_left} dia{'s' if days_left != 1 else ''})."
                        ),
                    )
                )

        if account.card_plafond is not None and account.current_balance < account.card_plafond:
            missing = account.card_plafond - account.current_balance
            insights.append(
                Insight(
                    rule="card_below_plafond",
                    severity=InsightSeverity.WARNING,
                    title=f"O cartão {account.name} está abaixo do plafond",
                    detail=(
                        f"Tem {_eur(account.current_balance)} de {_eur(account.card_plafond)} "
                        f"definidos — falta recarregar {_eur(missing)}."
                    ),
                )
            )

    insights.sort(key=lambda insight: _SEVERITY_ORDER[insight.severity])
    return insights
