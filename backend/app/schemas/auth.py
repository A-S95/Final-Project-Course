from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    # max_length=72: limite físico do bcrypt (bytes, não carateres — ver
    # ARCHITECTURE.md secção 8, "Autenticação"). Acima disto, o bcrypt
    # moderno levanta erro em vez de truncar silenciosamente como antes.
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
