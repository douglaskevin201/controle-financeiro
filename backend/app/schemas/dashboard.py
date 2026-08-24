from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CategorySummary(BaseModel):
    category_id: Optional[int]
    category_name: str
    color: str
    total: float
    percentage: float

class MonthlyData(BaseModel):
    month: int
    month_name: str
    income: float
    expense: float
    net: float

class DashboardSummary(BaseModel):
    # Saldos
    main_balance: float            # Saldo disponível na conta principal
    total_in_pockets: float        # Total guardado em todas as caixinhas
    total_wealth: float            # Saldo principal + Caixinhas
    
    # Mês Atual
    month: int
    year: int
    monthly_income: float
    monthly_expense: float
    monthly_net: float
    
    # Contas fixas do mês
    recurring_bills_total: float
    recurring_bills_paid: float
    recurring_bills_pending: float
    pending_bills_count: int

class DashboardCharts(BaseModel):
    expenses_by_category: List[CategorySummary]
    incomes_by_category: List[CategorySummary]
    monthly_evolution: List[MonthlyData]

