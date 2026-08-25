from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.database import Base


class FixedIncome(Base):
    __tablename__ = "fixed_incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    description = Column(String, nullable=False)
    base_amount = Column(Float, nullable=False)
    pay_day = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="fixed_incomes")
    category = relationship("Category", back_populates="fixed_incomes")
    receipts = relationship("FixedIncomeReceipt", back_populates="fixed_income", cascade="all, delete-orphan")


class FixedIncomeReceipt(Base):
    __tablename__ = "fixed_income_receipts"
    __table_args__ = (UniqueConstraint("fixed_income_id", "year", "month", name="uq_fixed_income_receipt_period"),)

    id = Column(Integer, primary_key=True, index=True)
    fixed_income_id = Column(Integer, ForeignKey("fixed_incomes.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    base_amount = Column(Float, nullable=False)
    extra_amount = Column(Float, default=0.0, nullable=False)
    received_amount = Column(Float, nullable=False)
    paid_at = Column(Date, default=date.today, nullable=False)
    status = Column(String, default="received", nullable=False)

    fixed_income = relationship("FixedIncome", back_populates="receipts")
    transaction = relationship("Transaction", back_populates="fixed_income_receipt")
