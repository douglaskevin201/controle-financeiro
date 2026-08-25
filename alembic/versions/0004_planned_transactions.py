"""Add planned transaction flag.

Revision ID: 0004_planned_transactions
Revises: 0003_installment_fields
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_planned_transactions"
down_revision = "0003_installment_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(sa.Column("is_planned", sa.Boolean(), nullable=False, server_default="0"))


def downgrade() -> None:
    pass
