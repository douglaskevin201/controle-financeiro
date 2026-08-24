from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryCreate, CategoryResponse
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categorias"])

@router.get("", response_model=List[CategoryResponse])
def list_categories(
    type: Optional[Literal["income", "expense"]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.user_id == None)
    )
    if type:
        query = query.filter(Category.type == type)
    
    return query.order_by(Category.name.asc()).all()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verifica se já existe uma categoria com o mesmo nome e tipo para o usuário
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name.ilike(category_in.name.strip()),
        Category.type == category_in.type
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já possui uma categoria com este nome e tipo."
        )
    
    new_category = Category(
        user_id=current_user.id,
        name=category_in.name.strip(),
        type=category_in.type,
        color=category_in.color or "#3B82F6",
        icon=category_in.icon or "tag"
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    
    db.delete(category)
    db.commit()
    return None

