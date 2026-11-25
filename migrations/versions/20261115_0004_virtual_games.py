"""Add virtual number games, markets, rounds, rates, and bets."""

from datetime import time

from alembic import op
import sqlalchemy as sa

from app.game_rules import panna_rows


revision = "20261115_0004"
down_revision = "20261106_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "game_markets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("open_time", sa.Time(), nullable=False),
        sa.Column("close_time", sa.Time(), nullable=False),
        sa.Column("active_days", sa.String(length=32), nullable=False),
        sa.Column("bet_cutoff_minutes", sa.Integer(), nullable=False),
        sa.Column("paused", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "game_rounds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("market_id", sa.Integer(), nullable=False),
        sa.Column("round_date", sa.Date(), nullable=False),
        sa.Column("open_panna", sa.String(length=3), nullable=True),
        sa.Column("open_digit", sa.Integer(), nullable=True),
        sa.Column("close_panna", sa.String(length=3), nullable=True),
        sa.Column("close_digit", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("rng_seed_commitment", sa.String(length=64), nullable=True),
        sa.Column("rng_seed", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["market_id"], ["game_markets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("market_id", "round_date", name="uq_game_round_market_date"),
    )
    op.create_index("ix_game_rounds_market_id", "game_rounds", ["market_id"])
    op.create_table(
        "game_pannas",
        sa.Column("panna", sa.String(length=3), nullable=False),
        sa.Column("type", sa.String(length=12), nullable=False),
        sa.Column("digit", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("panna"),
    )
    op.create_index("ix_game_pannas_type", "game_pannas", ["type"])
    op.create_table(
        "game_bet_types",
        sa.Column("code", sa.String(length=24), nullable=False),
        sa.Column("label", sa.String(length=40), nullable=False),
        sa.Column("win_per_10", sa.Integer(), nullable=False),
        sa.Column("min_points", sa.Integer(), nullable=False),
        sa.Column("max_points", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_table(
        "game_bets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("round_id", sa.Integer(), nullable=False),
        sa.Column("bet_type", sa.String(length=24), nullable=False),
        sa.Column("session", sa.String(length=8), nullable=False),
        sa.Column("selection", sa.String(length=16), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("win_per_10_snapshot", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("win_points", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("points > 0", name="ck_game_bets_positive_points"),
        sa.ForeignKeyConstraint(["bet_type"], ["game_bet_types.code"]),
        sa.ForeignKeyConstraint(["round_id"], ["game_rounds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_game_bets_idempotency"),
    )
    op.create_index("ix_game_bets_user_id", "game_bets", ["user_id"])
    op.create_index("ix_game_bets_round_id", "game_bets", ["round_id"])

    markets = sa.table(
        "game_markets",
        sa.column("name", sa.String),
        sa.column("open_time", sa.Time),
        sa.column("close_time", sa.Time),
        sa.column("active_days", sa.String),
        sa.column("bet_cutoff_minutes", sa.Integer),
        sa.column("paused", sa.Boolean),
        sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(
        markets,
        [
            {"name": name, "open_time": open, "close_time": close,
             "active_days": "0,1,2,3,4,5,6", "bet_cutoff_minutes": 10,
             "paused": False, "sort_order": position}
            for position, (name, open, close) in enumerate(
                [
                    ("Kalyan", time(10, 0), time(23, 0)),
                    ("Milan Day", time(10, 15), time(22, 45)),
                    ("Rajdhani Day", time(11, 0), time(22, 30)),
                    ("Night Star", time(12, 0), time(23, 30)),
                    ("Main Bazar", time(12, 30), time(23, 45)),
                ]
            )
        ],
    )
    bet_types = sa.table(
        "game_bet_types",
        sa.column("code", sa.String),
        sa.column("label", sa.String),
        sa.column("win_per_10", sa.Integer),
        sa.column("min_points", sa.Integer),
        sa.column("max_points", sa.Integer),
        sa.column("enabled", sa.Boolean),
    )
    op.bulk_insert(
        bet_types,
        [
            {"code": code, "label": label, "win_per_10": rate,
             "min_points": 10, "max_points": 10000, "enabled": True}
            for code, label, rate in [
                ("SINGLE_DIGIT", "Single Digit", 95),
                ("JODI", "Jodi Digit", 900),
                ("SINGLE_PANNA", "Single Panna", 1400),
                ("DOUBLE_PANNA", "Double Panna", 2800),
                ("TRIPLE_PANNA", "Triple Panna", 7000),
            ]
        ],
    )
    pannas = sa.table(
        "game_pannas",
        sa.column("panna", sa.String),
        sa.column("type", sa.String),
        sa.column("digit", sa.Integer),
    )
    op.bulk_insert(
        pannas,
        [{"panna": panna, "type": kind, "digit": digit}
         for panna, kind, digit in panna_rows()],
    )


def downgrade() -> None:
    op.drop_index("ix_game_bets_round_id", table_name="game_bets")
    op.drop_index("ix_game_bets_user_id", table_name="game_bets")
    op.drop_table("game_bets")
    op.drop_table("game_bet_types")
    op.drop_index("ix_game_pannas_type", table_name="game_pannas")
    op.drop_table("game_pannas")
    op.drop_index("ix_game_rounds_market_id", table_name="game_rounds")
    op.drop_table("game_rounds")
    op.drop_table("game_markets")
