from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nome da categoria")
    type: Literal["income", "expense"]
    color: Optional[str] = Field(default="#3B82F6", max_length=20)
    icon: Optional[str] = Field(default="tag", max_length=30)

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
