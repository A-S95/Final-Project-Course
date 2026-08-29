import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.household import InviteStatus


class HouseholdCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class InviteCreate(BaseModel):
    email: EmailStr


class HouseholdMemberRead(BaseModel):
    user_id: uuid.UUID
    name: str
    email: EmailStr
    joined_at: datetime
    is_creator: bool


class HouseholdRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_by: uuid.UUID
    created_at: datetime
    members: list[HouseholdMemberRead]


class InviteRead(BaseModel):
    """Serve os dois sentidos: convites enviados pelo meu agregado e convites que
    recebi. Os campos de nome/email são resolvidos no service."""

    id: uuid.UUID
    household_id: uuid.UUID
    household_name: str
    invited_user_email: EmailStr
    invited_user_name: str
    invited_by_name: str
    status: InviteStatus
    created_at: datetime
    responded_at: datetime | None
