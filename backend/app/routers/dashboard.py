from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.models.recurring_bill import RecurringBill, BillPayment
from backend.app.models.pocket import Pocket, PocketTransaction
from backend.app.models.fixed_income import FixedIncome
from backend.app.schemas.dashboard import DashboardSummary, DashboardCharts, CategorySummary, MonthlyData
from backend.app.schemas.projection import DashboardProjection
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

MONTH_NAMES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]

def next_period(month: int, year: int) -> tuple[int, int]:
    return (1, year + 1) if month == 12 else (month + 1, year)

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or date.today().month
    target_year = year or date.today().year

    # 1. Total histórico de receitas e despesas
    total_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.is_planned == False
    ).scalar()

    total_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.is_planned == False
    ).scalar()

    # 2. Total de depósitos e saques em caixinhas
    pocket_deposits = db.query(func.coalesce(func.sum(PocketTransaction.amount), 0.0)).filter(
        PocketTransaction.user_id == current_user.id,
        PocketTransaction.type == "deposit"
    ).scalar()

    pocket_withdraws = db.query(func.coalesce(func.sum(PocketTransaction.amount), 0.0)).filter(
        PocketTransaction.user_id == current_user.id,
        PocketTransaction.type == "withdraw"
    ).scalar()

    # Saldo principal disponível
    main_balance = total_income - total_expense - pocket_deposits + pocket_withdraws

    # 3. Total acumulado em caixinhas
    total_in_pockets = db.query(func.coalesce(func.sum(Pocket.current_amount), 0.0)).filter(
        Pocket.user_id == current_user.id
    ).scalar()

    total_wealth = main_balance + total_in_pockets

    # 4. Métricas do Mês Consultado
    monthly_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.is_planned == False,
        extract('year', Transaction.transaction_date) == target_year,
        extract('month', Transaction.transaction_date) == target_month
    ).scalar()

    monthly_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.is_planned == False,
        extract('year', Transaction.transaction_date) == target_year,
        extract('month', Transaction.transaction_date) == target_month
    ).scalar()

    monthly_net = monthly_income - monthly_expense

    fixed_income_expected = db.query(func.coalesce(func.sum(FixedIncome.base_amount), 0.0)).filter(
        FixedIncome.user_id == current_user.id,
        FixedIncome.is_active == True,
    ).scalar()

    # 5. Contas Fixas Recorrentes do Mês
    active_bills = db.query(RecurringBill).filter(
        RecurringBill.user_id == current_user.id,
        RecurringBill.is_active == True
    ).all()

    recurring_bills_total = sum(b.amount for b in active_bills)
    bill_ids = [b.id for b in active_bills]

    paid_payments = db.query(BillPayment).filter(
        BillPayment.bill_id.in_(bill_ids),
        BillPayment.year == target_year,
        BillPayment.month == target_month,
        BillPayment.status == "paid"
    ).all() if bill_ids else []

    paid_bill_ids = {p.bill_id for p in paid_payments}
    recurring_bills_paid = sum(b.amount for b in active_bills if b.id in paid_bill_ids)
    recurring_bills_pending = max(0.0, recurring_bills_total - recurring_bills_paid)
    pending_bills_count = len([b for b in active_bills if b.id not in paid_bill_ids])

    return DashboardSummary(
        main_balance=round(main_balance, 2),
        total_in_pockets=round(total_in_pockets, 2),
        total_wealth=round(total_wealth, 2),
        month=target_month,
        year=target_year,
        monthly_income=round(monthly_income, 2),
        monthly_expense=round(monthly_expense, 2),
        monthly_net=round(monthly_net, 2),
        fixed_income_expected=round(fixed_income_expected, 2),
        recurring_bills_total=round(recurring_bills_total, 2),
        recurring_bills_paid=round(recurring_bills_paid, 2),
        recurring_bills_pending=round(recurring_bills_pending, 2),
        pending_bills_count=pending_bills_count
    )

@router.get("/charts", response_model=DashboardCharts)
def get_dashboard_charts(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or date.today().month
    target_year = year or date.today().year

    # 1. Despesas por Categoria no Mês/Ano
    expense_query = db.query(
        Category.id.label("category_id"),
        Category.name.label("category_name"),
        Category.color.label("color"),
        func.sum(Transaction.amount).label("total")
    ).outerjoin(Category, Transaction.category_id == Category.id).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.is_planned == False,
        extract('year', Transaction.transaction_date) == target_year
    )
    if month:
        expense_query = expense_query.filter(extract('month', Transaction.transaction_date) == target_month)
    
    expense_results = expense_query.group_by(Category.id, Category.name, Category.color).all()
    total_expenses = sum(r.total for r in expense_results) or 1.0

    expenses_by_category = [
        CategorySummary(
            category_id=r.category_id,
            category_name=r.category_name or "Sem Categoria",
            color=r.color or "#94A3B8",
            total=round(r.total, 2),
            percentage=round((r.total / total_expenses) * 100, 1)
        )
        for r in expense_results
    ]

    # 2. Receitas por Categoria no Mês/Ano
    income_query = db.query(
        Category.id.label("category_id"),
        Category.name.label("category_name"),
        Category.color.label("color"),
        func.sum(Transaction.amount).label("total")
    ).outerjoin(Category, Transaction.category_id == Category.id).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.is_planned == False,
        extract('year', Transaction.transaction_date) == target_year
    )
    if month:
        income_query = income_query.filter(extract('month', Transaction.transaction_date) == target_month)

    income_results = income_query.group_by(Category.id, Category.name, Category.color).all()
    total_incomes = sum(r.total for r in income_results) or 1.0

    incomes_by_category = [
        CategorySummary(
            category_id=r.category_id,
            category_name=r.category_name or "Sem Categoria",
            color=r.color or "#10B981",
            total=round(r.total, 2),
            percentage=round((r.total / total_incomes) * 100, 1)
        )
        for r in income_results
    ]

    # 3. Evolução Mensal ao longo do Ano (12 meses)
    monthly_evolution = []
    for m in range(1, 13):
        m_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "income",
            Transaction.is_planned == False,
            extract('year', Transaction.transaction_date) == target_year,
            extract('month', Transaction.transaction_date) == m
        ).scalar()

        m_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.is_planned == False,
            extract('year', Transaction.transaction_date) == target_year,
            extract('month', Transaction.transaction_date) == m
        ).scalar()

        monthly_evolution.append(
            MonthlyData(
                month=m,
                month_name=MONTH_NAMES[m - 1],
                income=round(m_income, 2),
                expense=round(m_expense, 2),
                net=round(m_income - m_expense, 2)
            )
        )

    return DashboardCharts(
        expenses_by_category=expenses_by_category,
        incomes_by_category=incomes_by_category,
        monthly_evolution=monthly_evolution
    )


@router.get("/projection", response_model=DashboardProjection)
def get_dashboard_projection(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reference_month = month or date.today().month
    reference_year = year or date.today().year
    projection_month, projection_year = next_period(reference_month, reference_year)

    total_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id, Transaction.type == "income", Transaction.is_planned == False
    ).scalar()
    total_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id, Transaction.type == "expense", Transaction.is_planned == False
    ).scalar()
    pocket_deposits = db.query(func.coalesce(func.sum(PocketTransaction.amount), 0.0)).filter(
        PocketTransaction.user_id == current_user.id, PocketTransaction.type == "deposit"
    ).scalar()
    pocket_withdraws = db.query(func.coalesce(func.sum(PocketTransaction.amount), 0.0)).filter(
        PocketTransaction.user_id == current_user.id, PocketTransaction.type == "withdraw"
    ).scalar()
    current_main_balance = total_income - total_expense - pocket_deposits + pocket_withdraws

    fixed_income_expected = db.query(func.coalesce(func.sum(FixedIncome.base_amount), 0.0)).filter(
        FixedIncome.user_id == current_user.id, FixedIncome.is_active == True
    ).scalar()
    planned_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.is_planned == True,
        extract('year', Transaction.transaction_date) == projection_year,
        extract('month', Transaction.transaction_date) == projection_month,
    ).scalar()
    planned_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.is_planned == True,
        extract('year', Transaction.transaction_date) == projection_year,
        extract('month', Transaction.transaction_date) == projection_month,
    ).scalar()
    bills = db.query(RecurringBill).filter(
        RecurringBill.user_id == current_user.id, RecurringBill.is_active == True
    ).all()
    recurring_bills_expected = sum(
        bill.amount for bill in bills
        if (projection_year - (bill.start_year or projection_year)) * 12
        + projection_month - (bill.start_month or projection_month) in range(bill.installments_total)
    )
    projected_net = fixed_income_expected + planned_income - recurring_bills_expected - planned_expense
    return DashboardProjection(
        reference_month=reference_month,
        reference_year=reference_year,
        projection_month=projection_month,
        projection_year=projection_year,
        current_main_balance=round(current_main_balance, 2),
        fixed_income_expected=round(fixed_income_expected, 2),
        planned_income=round(planned_income, 2),
        planned_expense=round(planned_expense, 2),
        recurring_bills_expected=round(recurring_bills_expected, 2),
        projected_net=round(projected_net, 2),
        projected_main_balance=round(current_main_balance + projected_net, 2),
    )

