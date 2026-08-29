import uuid
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


def test_create_and_fetch_user(db_session: Session) -> None:
    user = User(
        email="antonio@example.com",
        password_hash="hashed",
        name="Antonio",
        monthly_income=Decimal("2500.50"),
    )
    db_session.add(user)
    db_session.flush()

    fetched = db_session.get(User, user.id)

    assert fetched is not None
    assert isinstance(fetched.id, uuid.UUID)
    assert fetched.email == "antonio@example.com"
    assert fetched.currency == "EUR"
    assert fetched.monthly_income == Decimal("2500.50")
    assert fetched.created_at is not None
    assert fetched.updated_at is not None


def test_email_must_be_unique(db_session: Session) -> None:
    db_session.add(User(email="dup@example.com", password_hash="x", name="A"))
    db_session.flush()

    db_session.add(User(email="dup@example.com", password_hash="y", name="B"))
    with pytest.raises(IntegrityError):
        db_session.flush()
