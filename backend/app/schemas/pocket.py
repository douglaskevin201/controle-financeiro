from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, date
from typing import Optional, Literal

class PocketBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: Optional[float] = Field(default=None, gt=0, description="Meta opcional")
    color: Optional[str] = Field(default="#10B981", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = "piggy-bank"

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O nome não pode ficar vazio.")
        return value

class PocketCreate(PocketBase):
    initial_deposit: Optional[float] = Field(default=0.0, ge=0)

class PocketUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    target_amount: Optional[float] = Field(default=None, gt=0)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("O nome não pode ficar vazio.")
        return value

class PocketTransactionResponse(BaseModel):
    id: int
    pocket_id: int
    user_id: int
    type: Literal["deposit", "withdraw"]
    amount: float
    description: Optional[str] = None
    transaction_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PocketResponse(PocketBase):
    id: int
    user_id: int
    current_amount: float
    progress_percentage: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PocketTransferRequest(BaseModel):
    type: Literal["deposit", "withdraw"] # deposit = guardar, withdraw = resgatar
    amount: float = Field(gt=0, description="Valor da movimentação")
    description: Optional[str] = Field(default=None, max_length=255)
    transaction_date: Optional[date] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value and value.strip() else None

