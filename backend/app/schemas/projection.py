from pydantic import BaseModel


class DashboardProjection(BaseModel):
    reference_month: int
    reference_year: int
    projection_month: int
    projection_year: int
    current_main_balance: float
    fixed_income_expected: float
    planned_income: float
    planned_expense: float
    recurring_bills_expected: float
    projected_net: float
    projected_main_balance: float
