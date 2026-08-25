from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, date
from typing import Optional, List
from backend.app.schemas.category import CategoryResponse

class RecurringBillBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(gt=0)
    total_amount: Optional[float] = Field(default=None, gt=0)
    installments_total: int = Field(default=1, ge=1, le=120)
    start_month: Optional[int] = Field(default=None, ge=1, le=12)
    start_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    due_day: int = Field(ge=1, le=31, description="Dia do vencimento entre 1 e 31")
    category_id: Optional[int] = None
    is_active: Optional[bool] = True

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A descrição não pode ficar vazia.")
        return value

class RecurringBillCreate(RecurringBillBase):
    pass

class RecurringBillUpdate(BaseModel):
    description: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[float] = Field(default=None, gt=0)
    total_amount: Optional[float] = Field(default=None, gt=0)
    installments_total: Optional[int] = Field(default=None, ge=1, le=120)
    start_month: Optional[int] = Field(default=None, ge=1, le=12)
    start_year: Optional[int] = Field(default=None, ge=2000, le=2100)
    due_day: Optional[int] = Field(default=None, ge=1, le=31)
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

class BillPaymentResponse(BaseModel):
    id: int
    bill_id: int
    year: int
    month: int
    status: str
    paid_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class RecurringBillResponse(RecurringBillBase):
    id: int
    user_id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None
    # Status calculado para o mês consultado
    is_paid_this_month: Optional[bool] = False
    payment_info: Optional[BillPaymentResponse] = None

    model_config = ConfigDict(from_attributes=True)

class PayBillRequest(BaseModel):
    paid_date: Optional[date] = None
    create_transaction: bool = True

