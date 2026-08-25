from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.schemas.category import CategoryResponse


class FixedIncomeCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    base_amount: float = Field(..., gt=0)
    pay_day: int = Field(..., ge=1, le=31)
    category_id: Optional[int] = None
    is_active: bool = True

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A descrição não pode ficar vazia.")
        return value


class FixedIncomeUpdate(BaseModel):
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    base_amount: Optional[float] = Field(default=None, gt=0)
    pay_day: Optional[int] = Field(default=None, ge=1, le=31)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("A descrição não pode ficar vazia.")
        return value


class FixedIncomeReceiptRequest(BaseModel):
    extra_amount: float = Field(default=0, ge=0)
    paid_date: Optional[date] = None


class FixedIncomeReceiptResponse(BaseModel):
    id: int
    fixed_income_id: int
    transaction_id: Optional[int] = None
    year: int
    month: int
    base_amount: float
    extra_amount: float
    received_amount: float
    paid_at: date
    status: str

    model_config = ConfigDict(from_attributes=True)


class FixedIncomeResponse(BaseModel):
    id: int
    user_id: int
    description: str
    base_amount: float
    pay_day: int
    category_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    category: Optional[CategoryResponse] = None
    is_received_this_month: bool = False
    receipt: Optional[FixedIncomeReceiptResponse] = None

    model_config = ConfigDict(from_attributes=True)
