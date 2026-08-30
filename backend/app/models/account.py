import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AccountType(enum.StrEnum):
    BANK = "BANK"
    WALLET = "WALLET"
    SAVINGS = "SAVINGS"
    CREDIT_CARD = "CREDIT_CARD"
    OTHER = "OTHER"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="account_type"), nullable=False
    )
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    # Mantido pelo service layer, nunca escrito diretamente por um request do cliente.
    current_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    # Ambos opcionais, nulos para contas que não são cartões; geram alerta em Insights
    # perto da validade, ou se current_balance cair abaixo do plafond esperado.
    card_expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    card_plafond: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
