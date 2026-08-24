from typing import List, Optional, Literal
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transações"])

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    type: Optional[Literal["income", "expense"]] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if year:
        query = query.filter(extract('year', Transaction.transaction_date) == year)
    if month:
        query = query.filter(extract('month', Transaction.transaction_date) == month)
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search.strip()}%"))

    return query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    trans_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validar se a categoria existe e pertence ao usuário (ou global)
    if trans_in.category_id:
        category = db.query(Category).filter(
            Category.id == trans_in.category_id,
            (Category.user_id == current_user.id) | (Category.user_id == None)
        ).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria inválida.")
    
    transaction_date = trans_in.transaction_date or date.today()

    new_tx = Transaction(
        user_id=current_user.id,
        category_id=trans_in.category_id,
        description=trans_in.description.strip(),
        amount=trans_in.amount,
        type=trans_in.type,
        transaction_date=transaction_date
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada.")
    return tx

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    trans_in: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada.")

    if trans_in.category_id is not None:
        if trans_in.category_id != 0:
            category = db.query(Category).filter(
                Category.id == trans_in.category_id,
                (Category.user_id == current_user.id) | (Category.user_id == None)
            ).first()
            if not category:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria inválida.")
            tx.category_id = trans_in.category_id
        else:
            tx.category_id = None

    if trans_in.description is not None:
        tx.description = trans_in.description.strip()
    if trans_in.amount is not None:
        tx.amount = trans_in.amount
    if trans_in.type is not None:
        tx.type = trans_in.type
    if trans_in.transaction_date is not None:
        tx.transaction_date = trans_in.transaction_date

    db.commit()
    db.refresh(tx)
    return tx

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transação não encontrada.")
    
    db.delete(tx)
    db.commit()
    return None

