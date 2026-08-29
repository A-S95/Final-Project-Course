import calendar
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import (
    RecurringExpenseCategoryInvalidError,
    RecurringExpenseNotFoundError,
)
from app.models.category import CategoryType
from app.models.recurring_expense import RecurringExpense, RecurringFrequency
from app.models.transaction import TransactionType
from app.repositories import recurring_expense_repository
from app.schemas.recurring_expense import RecurringExpenseRead, RecurringRunResult
from app.services import account_service, category_service, transaction_service

# Rede de segurança: no máximo isto de ocorrências geradas por recorrência numa
# só invocação (~10 anos de mensalidades) — protege contra um `next_occurrence`
# muito no passado por erro.
_MAX_CATCH_UP = 120


def _clamp_day(year: int, month: int, day_of_month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day_of_month, last_day))


def advance(current: date, day_of_month: int, frequency: RecurringFrequency) -> date:
    """Próxima data de ocorrência depois de `current`.

    Avança sempre a partir do `day_of_month` canónico (não de `current.day`), para
    que um mês curto não "encolha" a recorrência para sempre: 31/jan → 28/fev →
    31/mar.
    """
    if frequency == RecurringFrequency.MONTHLY:
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
    else:  # YEARLY
        year, month = current.year + 1, current.month
    return _clamp_day(year, month, day_of_month)


def _validate_refs(
    db: Session, *, user_id: uuid.UUID, account_id: uuid.UUID, category_id: uuid.UUID
) -> None:
    account_service.get_account(db, user_id=user_id, account_id=account_id)
    category = category_service.get_category(db, user_id=user_id, category_id=category_id)
    if category.type != CategoryType.EXPENSE:
        raise RecurringExpenseCategoryInvalidError


def _to_read(
    db: Session, recurring: RecurringExpense, *, user_id: uuid.UUID, today: date
) -> RecurringExpenseRead:
    account = account_service.get_account(
        db, user_id=user_id, account_id=recurring.account_id
    )
    category = category_service.get_category(
        db, user_id=user_id, category_id=recurring.category_id
    )
    return RecurringExpenseRead(
        id=recurring.id,
        account_id=recurring.account_id,
        account_name=account.name,
        category_id=recurring.category_id,
        category_name=category.name,
        description=recurring.description,
        amount=recurring.amount,
        frequency=recurring.frequency,
        day_of_month=recurring.day_of_month,
        next_occurrence=recurring.next_occurrence,
        active=recurring.active,
        is_due=recurring.active and recurring.next_occurrence <= today,
        created_at=recurring.created_at,
        updated_at=recurring.updated_at,
    )


def get_recurring(
    db: Session, *, user_id: uuid.UUID, recurring_id: uuid.UUID
) -> RecurringExpense:
    recurring = recurring_expense_repository.get_by_id_for_user(db, recurring_id, user_id)
    if recurring is None:
        raise RecurringExpenseNotFoundError
    return recurring


def list_recurring(db: Session, *, user_id: uuid.UUID) -> list[RecurringExpenseRead]:
    today = date.today()
    return [
        _to_read(db, recurring, user_id=user_id, today=today)
        for recurring in recurring_expense_repository.list_by_user(db, user_id)
    ]


def create_recurring(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID,
    category_id: uuid.UUID,
    description: str,
    amount: Decimal,
    frequency: RecurringFrequency,
    next_occurrence: date,
    active: bool,
) -> RecurringExpenseRead:
    _validate_refs(db, user_id=user_id, account_id=account_id, category_id=category_id)

    recurring = RecurringExpense(
        user_id=user_id,
        account_id=account_id,
        category_id=category_id,
        description=description,
        amount=amount,
        frequency=frequency,
        day_of_month=next_occurrence.day,
        next_occurrence=next_occurrence,
        active=active,
    )
    recurring_expense_repository.create(db, recurring)
    return _to_read(db, recurring, user_id=user_id, today=date.today())


def update_recurring(
    db: Session,
    *,
    user_id: uuid.UUID,
    recurring_id: uuid.UUID,
    account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
    description: str | None,
    amount: Decimal | None,
    frequency: RecurringFrequency | None,
    next_occurrence: date | None,
    active: bool | None,
) -> RecurringExpenseRead:
    recurring = get_recurring(db, user_id=user_id, recurring_id=recurring_id)

    if account_id is not None or category_id is not None:
        _validate_refs(
            db,
            user_id=user_id,
            account_id=account_id or recurring.account_id,
            category_id=category_id or recurring.category_id,
        )

    if account_id is not None:
        recurring.account_id = account_id
    if category_id is not None:
        recurring.category_id = category_id
    if description is not None:
        recurring.description = description
    if amount is not None:
        recurring.amount = amount
    if frequency is not None:
        recurring.frequency = frequency
    if next_occurrence is not None:
        recurring.next_occurrence = next_occurrence
        recurring.day_of_month = next_occurrence.day
    if active is not None:
        recurring.active = active

    db.flush()
    return _to_read(db, recurring, user_id=user_id, today=date.today())


def delete_recurring(db: Session, *, user_id: uuid.UUID, recurring_id: uuid.UUID) -> None:
    recurring = get_recurring(db, user_id=user_id, recurring_id=recurring_id)
    recurring_expense_repository.delete(db, recurring)
    db.flush()


def generate_due(
    db: Session, *, user_id: uuid.UUID, today: date | None = None
) -> RecurringRunResult:
    """Percorre as recorrências ativas com ocorrências por gerar e cria as transações
    em falta, apanhando o atraso se a função não for chamada há vários meses.

    Cada transação passa pelo `transaction_service` normal, por isso os saldos das
    contas ficam sempre consistentes — a geração não é um caminho especial.
    """
    today = today or date.today()
    generated = 0

    for recurring in recurring_expense_repository.list_due_for_user(db, user_id, today):
        category = category_service.get_category(
            db, user_id=user_id, category_id=recurring.category_id
        )
        if category.type != CategoryType.EXPENSE:
            # Estado inconsistente (a categoria mudou de tipo depois de criada a
            # recorrência) — não geramos nada; fica visível como "em atraso".
            continue

        iterations = 0
        while recurring.next_occurrence <= today and iterations < _MAX_CATCH_UP:
            transaction_service.create_transaction(
                db,
                user_id=user_id,
                account_id=recurring.account_id,
                destination_account_id=None,
                category_id=recurring.category_id,
                type=TransactionType.EXPENSE,
                amount=recurring.amount,
                description=recurring.description,
                date=recurring.next_occurrence,
            )
            recurring.next_occurrence = advance(
                recurring.next_occurrence, recurring.day_of_month, recurring.frequency
            )
            generated += 1
            iterations += 1

    db.flush()
    return RecurringRunResult(generated=generated)
