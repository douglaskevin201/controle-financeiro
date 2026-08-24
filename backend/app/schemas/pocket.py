from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, Literal

class PocketBase(BaseModel):
    name: str
    target_amount: Optional[float] = Field(default=None, gt=0, description="Meta opcional")
    color: Optional[str] = "#10B981"
    icon: Optional[str] = "piggy-bank"

class PocketCreate(PocketBase):
    initial_deposit: Optional[float] = Field(default=0.0, ge=0)

class PocketUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = Field(default=None, gt=0)
    color: Optional[str] = None
    icon: Optional[str] = None

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
    description: Optional[str] = None
    transaction_date: Optional[date] = None

