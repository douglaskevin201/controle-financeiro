from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.recurring_bill import RecurringBill, BillPayment
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.schemas.recurring_bill import (
    RecurringBillCreate,
    RecurringBillUpdate,
    RecurringBillResponse,
    BillPaymentResponse,
    PayBillRequest
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/recurring-bills", tags=["Contas Recorrentes"])

def bill_applies_to_period(bill: RecurringBill, month: int, year: int) -> bool:
    if not bill.start_month or not bill.start_year or bill.installments_total <= 1:
        return True
    period = (year - bill.start_year) * 12 + month - bill.start_month
    return 0 <= period < bill.installments_total

@router.get("", response_model=List[RecurringBillResponse])
def list_recurring_bills(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or date.today().month
    target_year = year or date.today().year

    query = db.query(RecurringBill).filter(RecurringBill.user_id == current_user.id)
    if active_only:
        query = query.filter(RecurringBill.is_active == True)

    bills = query.order_by(RecurringBill.due_day.asc()).all()
    bills = [bill for bill in bills if bill_applies_to_period(bill, target_month, target_year)]

    # Busca os pagamentos do mês selecionado
    bill_ids = [b.id for b in bills]
    payments = db.query(BillPayment).filter(
        BillPayment.bill_id.in_(bill_ids),
        BillPayment.year == target_year,
        BillPayment.month == target_month
    ).all() if bill_ids else []

    payment_map = {p.bill_id: p for p in payments}

    results = []
    for bill in bills:
        payment = payment_map.get(bill.id)
        is_paid = payment is not None and payment.status == "paid"
        
        bill_dict = RecurringBillResponse(
            id=bill.id,
            user_id=bill.user_id,
            description=bill.description,
            amount=bill.amount,
            total_amount=bill.total_amount or bill.amount,
            installments_total=bill.installments_total,
            start_month=bill.start_month,
            start_year=bill.start_year,
            due_day=bill.due_day,
            category_id=bill.category_id,
            is_active=bill.is_active,
            created_at=bill.created_at,
            category=bill.category,
            is_paid_this_month=is_paid,
            payment_info=BillPaymentResponse.model_validate(payment) if payment else None
        )
        results.append(bill_dict)

    return results

@router.post("", response_model=RecurringBillResponse, status_code=status.HTTP_201_CREATED)
def create_recurring_bill(
    bill_in: RecurringBillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if bill_in.category_id:
        cat = db.query(Category).filter(
            Category.id == bill_in.category_id,
            (Category.user_id == current_user.id) | (Category.user_id == None)
        ).first()
        if not cat:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria inválida.")
        if cat.type != "expense":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A conta deve usar uma categoria de despesa.")

    total_amount = bill_in.total_amount or bill_in.amount
    installment_amount = round(total_amount / bill_in.installments_total, 2)
    new_bill = RecurringBill(
        user_id=current_user.id,
        category_id=bill_in.category_id,
        description=bill_in.description.strip(),
        amount=installment_amount,
        total_amount=total_amount,
        installments_total=bill_in.installments_total,
        start_month=bill_in.start_month or date.today().month,
        start_year=bill_in.start_year or date.today().year,
        due_day=bill_in.due_day,
        is_active=bill_in.is_active if bill_in.is_active is not None else True
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return RecurringBillResponse(
        id=new_bill.id,
        user_id=new_bill.user_id,
        description=new_bill.description,
        amount=new_bill.amount,
        total_amount=new_bill.total_amount,
        installments_total=new_bill.installments_total,
        start_month=new_bill.start_month,
        start_year=new_bill.start_year,
        due_day=new_bill.due_day,
        category_id=new_bill.category_id,
        is_active=new_bill.is_active,
        created_at=new_bill.created_at,
        category=new_bill.category,
        is_paid_this_month=False,
        payment_info=None
    )

@router.post("/{bill_id}/pay", response_model=RecurringBillResponse)
def pay_recurring_bill(
    bill_id: int,
    pay_data: PayBillRequest,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or date.today().month
    target_year = year or date.today().year
    pay_date = pay_data.paid_date or date.today()
    if pay_date.month != target_month or pay_date.year != target_year:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data de pagamento deve pertencer ao mês selecionado.")

    bill = db.query(RecurringBill).filter(
        RecurringBill.id == bill_id,
        RecurringBill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta fixa não encontrada.")

    # Verifica se já está paga no mês
    payment = db.query(BillPayment).filter(
        BillPayment.bill_id == bill_id,
        BillPayment.year == target_year,
        BillPayment.month == target_month
    ).first()

    if payment and payment.status == "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta conta já está marcada como paga neste mês.")

    transaction_id = None
    if pay_data.create_transaction:
        # Cria uma transação de despesa vinculada
        new_tx = Transaction(
            user_id=current_user.id,
            category_id=bill.category_id,
            description=f"Pagamento: {bill.description}",
            amount=bill.amount,
            type="expense",
            transaction_date=pay_date
        )
        db.add(new_tx)
        db.flush()
        transaction_id = new_tx.id

    if not payment:
        payment = BillPayment(
            bill_id=bill.id,
            transaction_id=transaction_id,
            year=target_year,
            month=target_month,
            status="paid",
            paid_at=pay_date
        )
        db.add(payment)
    else:
        payment.status = "paid"
        payment.paid_at = pay_date
        payment.transaction_id = transaction_id

    db.commit()
    db.refresh(payment)

    return RecurringBillResponse(
        id=bill.id,
        user_id=bill.user_id,
        description=bill.description,
        amount=bill.amount,
        total_amount=bill.total_amount or bill.amount,
        installments_total=bill.installments_total,
        start_month=bill.start_month,
        start_year=bill.start_year,
        due_day=bill.due_day,
        category_id=bill.category_id,
        is_active=bill.is_active,
        created_at=bill.created_at,
        category=bill.category,
        is_paid_this_month=True,
        payment_info=BillPaymentResponse.model_validate(payment)
    )

@router.post("/{bill_id}/unpay", response_model=RecurringBillResponse)
def unpay_recurring_bill(
    bill_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or date.today().month
    target_year = year or date.today().year

    bill = db.query(RecurringBill).filter(
        RecurringBill.id == bill_id,
        RecurringBill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta fixa não encontrada.")

    payment = db.query(BillPayment).filter(
        BillPayment.bill_id == bill_id,
        BillPayment.year == target_year,
        BillPayment.month == target_month
    ).first()

    if payment:
        # Se tiver transação de despesa criada automaticamente, removemos também
        if payment.transaction_id:
            tx = db.query(Transaction).filter(
                Transaction.id == payment.transaction_id,
                Transaction.user_id == current_user.id
            ).first()
            if tx:
                db.delete(tx)
        db.delete(payment)
        db.commit()

    return RecurringBillResponse(
        id=bill.id,
        user_id=bill.user_id,
        description=bill.description,
        amount=bill.amount,
        total_amount=bill.total_amount or bill.amount,
        installments_total=bill.installments_total,
        start_month=bill.start_month,
        start_year=bill.start_year,
        due_day=bill.due_day,
        category_id=bill.category_id,
        is_active=bill.is_active,
        created_at=bill.created_at,
        category=bill.category,
        is_paid_this_month=False,
        payment_info=None
    )

@router.put("/{bill_id}", response_model=RecurringBillResponse)
def update_recurring_bill(
    bill_id: int,
    bill_in: RecurringBillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(RecurringBill).filter(
        RecurringBill.id == bill_id,
        RecurringBill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta fixa não encontrada.")

    if bill_in.category_id is not None:
        if bill_in.category_id != 0:
            cat = db.query(Category).filter(
                Category.id == bill_in.category_id,
                (Category.user_id == current_user.id) | (Category.user_id == None)
            ).first()
            if not cat:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria inválida.")
            if cat.type != "expense":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A conta deve usar uma categoria de despesa.")
            bill.category_id = bill_in.category_id
        else:
            bill.category_id = None

    if bill_in.description is not None:
        bill.description = bill_in.description.strip()
    if bill_in.amount is not None:
        bill.amount = bill_in.amount
    if bill_in.total_amount is not None:
        bill.total_amount = bill_in.total_amount
    if bill_in.installments_total is not None:
        bill.installments_total = bill_in.installments_total
    if bill_in.start_month is not None:
        bill.start_month = bill_in.start_month
    if bill_in.start_year is not None:
        bill.start_year = bill_in.start_year
    if bill_in.due_day is not None:
        bill.due_day = bill_in.due_day
    if bill_in.is_active is not None:
        bill.is_active = bill_in.is_active
    if bill_in.total_amount is not None or bill_in.installments_total is not None:
        bill.total_amount = bill.total_amount or bill.amount
        bill.amount = round(bill.total_amount / bill.installments_total, 2)

    db.commit()
    db.refresh(bill)
    return RecurringBillResponse(
        id=bill.id,
        user_id=bill.user_id,
        description=bill.description,
        amount=bill.amount,
        total_amount=bill.total_amount or bill.amount,
        installments_total=bill.installments_total,
        start_month=bill.start_month,
        start_year=bill.start_year,
        due_day=bill.due_day,
        category_id=bill.category_id,
        is_active=bill.is_active,
        created_at=bill.created_at,
        category=bill.category,
        is_paid_this_month=False,
        payment_info=None
    )

@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(RecurringBill).filter(
        RecurringBill.id == bill_id,
        RecurringBill.user_id == current_user.id
    ).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta fixa não encontrada.")
    
    db.delete(bill)
    db.commit()
    return None

