from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, Literal
from backend.app.schemas.category import CategoryResponse

class TransactionBase(BaseModel):
    description: str
    amount: float = Field(gt=0, description="O valor deve ser maior que zero")
    type: Literal["income", "expense"]
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category_id: Optional[int] = None
    transaction_date: Optional[date] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)

