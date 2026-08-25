"""Ensure fixed income tables exist for databases created before salary support.

Revision ID: 0002_fixed_income
Revises: 0001_initial_schema
"""
from alembic import op
from sqlalchemy import inspect

from backend.app.models.fixed_income import FixedIncome, FixedIncomeReceipt

revision = "0002_fixed_income"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = set(inspector.get_table_names())
    if FixedIncome.__tablename__ not in existing:
        FixedIncome.__table__.create(bind=bind)
    if FixedIncomeReceipt.__tablename__ not in existing:
        FixedIncomeReceipt.__table__.create(bind=bind)


def downgrade() -> None:
    pass
