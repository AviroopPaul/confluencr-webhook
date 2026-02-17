"""create transactions

Revision ID: 0001_create_transactions
Revises: 
Create Date: 2026-02-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_create_transactions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_id", sa.String(length=64), nullable=False),
        sa.Column("source_account", sa.String(length=64), nullable=False),
        sa.Column("destination_account", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PROCESSING", "PROCESSED", "FAILED", name="txstatus"),
            nullable=False,
            server_default="PROCESSING",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_transactions_transaction_id", "transactions", ["transaction_id"], unique=True)
    op.create_index("ix_transactions_status", "transactions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_transactions_status", table_name="transactions")
    op.drop_index("ix_transactions_transaction_id", table_name="transactions")
    op.drop_table("transactions")
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS txstatus")
