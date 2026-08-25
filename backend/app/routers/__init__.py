from backend.app.routers.auth import router as auth_router
from backend.app.routers.categories import router as categories_router
from backend.app.routers.transactions import router as transactions_router
from backend.app.routers.recurring_bills import router as recurring_bills_router
from backend.app.routers.pockets import router as pockets_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.fixed_incomes import router as fixed_incomes_router

__all__ = [
    "auth_router",
    "categories_router",
    "transactions_router",
    "recurring_bills_router",
    "pockets_router",
    "dashboard_router",
    "fixed_incomes_router"
]

