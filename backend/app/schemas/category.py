from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal

class CategoryBase(BaseModel):
    name: str
    type: Literal["income", "expense"]
    color: Optional[str] = "#3B82F6"
    icon: Optional[str] = "tag"

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

