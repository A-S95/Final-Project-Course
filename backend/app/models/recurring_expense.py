import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RecurringFrequency(enum.StrEnum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_recurring_expenses_amount_positive"),
        CheckConstraint(
            "day_of_month BETWEEN 1 AND 31", name="ck_recurring_expenses_day_of_month"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # `RESTRICT` (ver ARCHITECTURE.md secção 5) — eliminar a conta/categoria com
    # despesas recorrentes associadas devolve 409, tal como com transações.
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    frequency: Mapped[RecurringFrequency] = mapped_column(
        Enum(RecurringFrequency, name="recurring_frequency"), nullable=False
    )
    # Dia "canónico" do mês (1–31). Guardado à parte do `next_occurrence.day` para
    # não perder o dia 31 quando um mês tem menos dias: fevereiro avança para 28,
    # mas março volta a 31.
    day_of_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    next_occurrence: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
