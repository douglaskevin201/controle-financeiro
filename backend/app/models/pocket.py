from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Pocket(Base):
    __tablename__ = "pockets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=True) # Meta opcional
    current_amount = Column(Float, default=0.0, nullable=False) # Saldo acumulado na caixinha
    color = Column(String, default="#10B981")
    icon = Column(String, default="piggy-bank")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="pockets")
    transactions = relationship("PocketTransaction", back_populates="pocket", cascade="all, delete-orphan")

class PocketTransaction(Base):
    __tablename__ = "pocket_transactions"

    id = Column(Integer, primary_key=True, index=True)
    pocket_id = Column(Integer, ForeignKey("pockets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # 'deposit' (guardar) ou 'withdraw' (resgatar)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    transaction_date = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="pocket_transactions")
    pocket = relationship("Pocket", back_populates="transactions")

