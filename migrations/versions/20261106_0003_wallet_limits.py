"""Use wide integer coin balances and enforce nonnegative balances."""

from alembic import op
import sqlalchemy as sa


revision = "20261106_0003"
down_revision = "20261106_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "coin_balance",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.create_check_constraint(
        "ck_users_nonnegative_coin_balance", "users", "coin_balance >= 0"
    )
    for column in ("amount_delta", "balance_after"):
        op.alter_column(
            "coin_transactions",
            column,
            existing_type=sa.Integer(),
            type_=sa.BigInteger(),
            existing_nullable=False,
        )


def downgrade() -> None:
    for column in ("amount_delta", "balance_after"):
        op.alter_column(
            "coin_transactions",
            column,
            existing_type=sa.BigInteger(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
    op.drop_constraint("ck_users_nonnegative_coin_balance", "users", type_="check")
    op.alter_column(
        "users",
        "coin_balance",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
