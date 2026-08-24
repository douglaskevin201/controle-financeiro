import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.models import (
    User, Category, Transaction, RecurringBill, BillPayment, Pocket, PocketTransaction
)
from backend.app.routers import (
    auth_router,
    categories_router,
    transactions_router,
    recurring_bills_router,
    pockets_router,
    dashboard_router
)

# Cria todas as tabelas no banco de dados SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API REST para Sistema de Controle Financeiro Pessoal com Caixinhas e Contas Fixas",
    version="1.0.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos Routers da API
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(recurring_bills_router)
app.include_router(pockets_router)

# Configuração para servir o Frontend estático
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/login")
    def serve_frontend_login():
        return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

