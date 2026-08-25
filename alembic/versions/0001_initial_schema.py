"""Create the initial schema without removing existing tables.

Revision ID: 0001_initial_schema
Revises:
"""
from alembic import op

from backend.app.database import Base
from backend.app import models  # noqa: F401

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # create_all is additive and preserves existing user data during the baseline
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    # The baseline is intentionally irreversible to avoid destructive data loss.
    pass
