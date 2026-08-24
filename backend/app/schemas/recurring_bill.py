from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from backend.app.schemas.category import CategoryResponse

class RecurringBillBase(BaseModel):
    description: str
    amount: float = Field(gt=0)
    due_day: int = Field(ge=1, le=31, description="Dia do vencimento entre 1 e 31")
    category_id: Optional[int] = None
    is_active: Optional[bool] = True

class RecurringBillCreate(RecurringBillBase):
    pass

class RecurringBillUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    due_day: Optional[int] = Field(default=None, ge=1, le=31)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

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

