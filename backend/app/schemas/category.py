from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Literal

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nome da categoria")
    type: Literal["income", "expense"]
    color: Optional[str] = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(default="tag", max_length=30)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O nome não pode ficar vazio.")
        return value

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
