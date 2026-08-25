from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional, Literal
from backend.app.schemas.category import CategoryResponse

class TransactionBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(gt=0, description="O valor deve ser maior que zero")
    type: Literal["income", "expense"]
    is_planned: bool = False
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A descrição não pode ficar vazia.")
        return value

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    is_planned: Optional[bool] = None
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("A descrição não pode ficar vazia.")
        return value

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)

