import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
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
    dashboard_router,
)
from backend.app.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Cria todas as tabelas no banco de dados SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API REST para Sistema de Controle Financeiro Pessoal com Caixinhas e Contas Fixas",
    version="1.0.0",
)

# HTTPS redirect in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Security headers middleware (simple implementation)
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    # CSP, HSTS, etc. only in production
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# SlowAPI middleware for global rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configuração de CORS usando origens definidas no .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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

