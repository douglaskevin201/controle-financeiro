"""Add installment metadata to recurring bills.

Revision ID: 0003_installment_fields
Revises: 0002_fixed_income
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_installment_fields"
down_revision = "0002_fixed_income"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("recurring_bills") as batch_op:
        batch_op.add_column(sa.Column("total_amount", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("installments_total", sa.Integer(), nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("start_month", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("start_year", sa.Integer(), nullable=True))


def downgrade() -> None:
    pass
