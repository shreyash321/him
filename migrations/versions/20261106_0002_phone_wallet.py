"""Add phone accounts, roles, and virtual coin ledger."""

from alembic import op
import sqlalchemy as sa


revision = "20261106_0002"
down_revision = "20261106_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.String(length=320), nullable=True)
    op.add_column("users", sa.Column("username", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=16), nullable=True))
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=16), nullable=False, server_default="user"),
    )
    op.add_column(
        "users",
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "users",
        sa.Column("coin_balance", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    op.create_table(
        "coin_transactions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("kind", sa.String(length=24), nullable=False),
        sa.Column("amount_delta", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=240), nullable=False),
        sa.Column("market", sa.String(length=80), nullable=True),
        sa.Column("selection", sa.String(length=80), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("amount_delta != 0", name="ck_coin_transactions_nonzero_delta"),
        sa.CheckConstraint(
            "balance_after >= 0", name="ck_coin_transactions_nonnegative_balance"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_coin_transactions_user_id", "coin_transactions", ["user_id"])
    op.create_index(
        "ix_coin_transactions_actor_user_id", "coin_transactions", ["actor_user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_coin_transactions_actor_user_id", table_name="coin_transactions")
    op.drop_index("ix_coin_transactions_user_id", table_name="coin_transactions")
    op.drop_table("coin_transactions")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.execute(
        "UPDATE users SET email = 'legacy-' || id || '@example.invalid' WHERE email IS NULL"
    )
    op.drop_column("users", "coin_balance")
    op.drop_column("users", "must_change_password")
    op.drop_column("users", "role")
    op.drop_column("users", "phone")
    op.drop_column("users", "username")
    op.alter_column("users", "email", existing_type=sa.String(length=320), nullable=False)
