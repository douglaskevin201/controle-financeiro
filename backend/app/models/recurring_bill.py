from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class RecurringBill(Base):
    __tablename__ = "recurring_bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=True)
    installments_total = Column(Integer, default=1, nullable=False)
    start_month = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True)
    due_day = Column(Integer, nullable=False) # 1 a 31
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="recurring_bills")
    category = relationship("Category", back_populates="recurring_bills")
    payments = relationship("BillPayment", back_populates="bill", cascade="all, delete-orphan")

class BillPayment(Base):
    __tablename__ = "bill_payments"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("recurring_bills.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    status = Column(String, default="paid") # 'pending', 'paid'
    paid_at = Column(Date, default=date.today)

    bill = relationship("RecurringBill", back_populates="payments")
    transaction = relationship("Transaction", back_populates="bill_payment")

