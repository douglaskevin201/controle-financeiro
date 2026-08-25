from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., max_length=255, description="Endereço de e-mail válido")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")
        return value

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="Senha forte com no mínimo 6 caracteres")
    admin_password: Optional[str] = Field(None, description="Senha secreta para tornar a conta admin")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
