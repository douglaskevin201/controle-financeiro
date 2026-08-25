from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.category import Category
from backend.app.models.fixed_income import FixedIncome, FixedIncomeReceipt
from backend.app.models.transaction import Transaction
from backend.app.models.user import User
from backend.app.schemas.fixed_income import (
    FixedIncomeCreate,
    FixedIncomeReceiptRequest,
    FixedIncomeReceiptResponse,
    FixedIncomeResponse,
    FixedIncomeUpdate,
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/fixed-incomes", tags=["Rendas Fixas"])


def get_owned_income(income_id: int, user_id: int, db: Session) -> FixedIncome:
    income = db.query(FixedIncome).filter(
        FixedIncome.id == income_id,
        FixedIncome.user_id == user_id,
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Renda fixa não encontrada.")
    return income


def validate_income_category(category_id: Optional[int], user: User, db: Session) -> None:
    if category_id is None:
        return
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.type == "income",
        (Category.user_id == user.id) | (Category.user_id == None),
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="A categoria deve ser uma categoria de receita válida.")


def serialize_income(income: FixedIncome, month: int, year: int) -> FixedIncomeResponse:
    receipt = next((item for item in income.receipts if item.month == month and item.year == year), None)
    return FixedIncomeResponse(
        id=income.id,
        user_id=income.user_id,
        description=income.description,
        base_amount=income.base_amount,
        pay_day=income.pay_day,
        category_id=income.category_id,
        is_active=bool(income.is_active),
        created_at=income.created_at,
        category=income.category,
        is_received_this_month=receipt is not None and receipt.status == "received",
        receipt=FixedIncomeReceiptResponse.model_validate(receipt) if receipt else None,
    )


@router.get("", response_model=List[FixedIncomeResponse])
def list_fixed_incomes(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_month = month or date.today().month
    target_year = year or date.today().year
    query = db.query(FixedIncome).filter(FixedIncome.user_id == current_user.id)
    if active_only:
        query = query.filter(FixedIncome.is_active == True)
    incomes = query.order_by(FixedIncome.pay_day.asc(), FixedIncome.id.asc()).all()
    return [serialize_income(item, target_month, target_year) for item in incomes]


@router.post("", response_model=FixedIncomeResponse, status_code=status.HTTP_201_CREATED)
def create_fixed_income(
    income_in: FixedIncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_income_category(income_in.category_id, current_user, db)
    income = FixedIncome(
        user_id=current_user.id,
        category_id=income_in.category_id,
        description=income_in.description,
        base_amount=income_in.base_amount,
        pay_day=income_in.pay_day,
        is_active=income_in.is_active,
    )
    db.add(income)
    db.commit()
    db.refresh(income)
    return serialize_income(income, date.today().month, date.today().year)


@router.put("/{income_id}", response_model=FixedIncomeResponse)
def update_fixed_income(
    income_id: int,
    income_in: FixedIncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = get_owned_income(income_id, current_user.id, db)
    if income_in.category_id is not None:
        validate_income_category(income_in.category_id, current_user, db)
        income.category_id = income_in.category_id or None
    if income_in.description is not None:
        income.description = income_in.description
    if income_in.base_amount is not None:
        income.base_amount = income_in.base_amount
    if income_in.pay_day is not None:
        income.pay_day = income_in.pay_day
    if income_in.is_active is not None:
        income.is_active = income_in.is_active
    db.commit()
    db.refresh(income)
    return serialize_income(income, date.today().month, date.today().year)


@router.post("/{income_id}/receive", response_model=FixedIncomeResponse)
def receive_fixed_income(
    income_id: int,
    receipt_in: FixedIncomeReceiptRequest,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_month = month or date.today().month
    target_year = year or date.today().year
    income = get_owned_income(income_id, current_user.id, db)
    paid_date = receipt_in.paid_date or date.today()
    received_amount = round(income.base_amount + receipt_in.extra_amount, 2)
    receipt = db.query(FixedIncomeReceipt).filter(
        FixedIncomeReceipt.fixed_income_id == income.id,
        FixedIncomeReceipt.month == target_month,
        FixedIncomeReceipt.year == target_year,
    ).first()

    if receipt and receipt.transaction_id:
        transaction = db.query(Transaction).filter(
            Transaction.id == receipt.transaction_id,
            Transaction.user_id == current_user.id,
        ).first()
        if transaction:
            transaction.amount = received_amount
            transaction.transaction_date = paid_date
            transaction.description = f"Recebimento: {income.description}"
    else:
        transaction = Transaction(
            user_id=current_user.id,
            category_id=income.category_id,
            description=f"Recebimento: {income.description}",
            amount=received_amount,
            type="income",
            transaction_date=paid_date,
        )
        db.add(transaction)
        db.flush()
        if receipt:
            receipt.transaction_id = transaction.id

    if not receipt:
        receipt = FixedIncomeReceipt(
            fixed_income_id=income.id,
            transaction_id=transaction.id,
            year=target_year,
            month=target_month,
            base_amount=income.base_amount,
            extra_amount=receipt_in.extra_amount,
            received_amount=received_amount,
            paid_at=paid_date,
            status="received",
        )
        db.add(receipt)
    else:
        receipt.base_amount = income.base_amount
        receipt.extra_amount = receipt_in.extra_amount
        receipt.received_amount = received_amount
        receipt.paid_at = paid_date
        receipt.status = "received"

    db.commit()
    db.refresh(income)
    return serialize_income(income, target_month, target_year)


@router.post("/{income_id}/unreceive", response_model=FixedIncomeResponse)
def unreceive_fixed_income(
    income_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_month = month or date.today().month
    target_year = year or date.today().year
    income = get_owned_income(income_id, current_user.id, db)
    receipt = db.query(FixedIncomeReceipt).filter(
        FixedIncomeReceipt.fixed_income_id == income.id,
        FixedIncomeReceipt.month == target_month,
        FixedIncomeReceipt.year == target_year,
    ).first()
    if receipt:
        if receipt.transaction_id:
            transaction = db.query(Transaction).filter(
                Transaction.id == receipt.transaction_id,
                Transaction.user_id == current_user.id,
            ).first()
            if transaction:
                db.delete(transaction)
        db.delete(receipt)
        db.commit()
        db.refresh(income)
    return serialize_income(income, target_month, target_year)


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixed_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = get_owned_income(income_id, current_user.id, db)
    db.delete(income)
    db.commit()
    return None
