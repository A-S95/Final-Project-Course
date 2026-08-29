import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: CategoryType
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=30)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: CategoryType | None = None
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=30)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: CategoryType
    icon: str | None
    color: str | None
    created_at: datetime
    updated_at: datetime
