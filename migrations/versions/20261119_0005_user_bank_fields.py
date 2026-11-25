"""Add bank/account fields to users table."""

from alembic import op
import sqlalchemy as sa


revision = "20261119_0005"
down_revision = "20261115_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("account_holder_name", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("bank_account_number", sa.String(length=40), nullable=True))
    op.add_column("users", sa.Column("ifsc_code", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "ifsc_code")
    op.drop_column("users", "bank_account_number")
    op.drop_column("users", "account_holder_name")
