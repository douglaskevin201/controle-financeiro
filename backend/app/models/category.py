from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True) # Nullable para categorias padrão
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # 'income' ou 'expense'
    color = Column(String, default="#3B82F6")
    icon = Column(String, default="tag")

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    recurring_bills = relationship("RecurringBill", back_populates="category")
    fixed_incomes = relationship("FixedIncome", back_populates="category")

