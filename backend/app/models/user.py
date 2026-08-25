from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    revoked_tokens = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relacionamentos
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    recurring_bills = relationship("RecurringBill", back_populates="user", cascade="all, delete-orphan")
    pockets = relationship("Pocket", back_populates="user", cascade="all, delete-orphan")
    pocket_transactions = relationship("PocketTransaction", back_populates="user", cascade="all, delete-orphan")
    fixed_incomes = relationship("FixedIncome", back_populates="user", cascade="all, delete-orphan")

