import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    currency: str
    monthly_income: Decimal | None


class UserUpdate(BaseModel):
    """Corpo do `PATCH /users/me`.

    Ao contrário de `AccountUpdate`/`CategoryUpdate` (edição de uma linha,
    campo a campo, com `None` a significar "não mexer"), a página de Settings
    submete sempre o formulário completo de uma vez — por isso `name` e
    `currency` são obrigatórios aqui. `monthly_income` continua opcional:
    `None` tem um significado de domínio válido ("sem rendimento definido"),
    não "não enviado".
    """

    name: str = Field(min_length=1, max_length=100)
    # ISO 4217 (EUR, USD, ...) — só a forma é validada aqui; a lista de
    # moedas suportadas na UI vive no frontend (features/auth/types.ts).
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    monthly_income: Decimal | None = Field(default=None, max_digits=12, decimal_places=2, ge=0)
