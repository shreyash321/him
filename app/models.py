from datetime import date, datetime, time
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("coin_balance >= 0", name="ck_users_nonnegative_coin_balance"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(16), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(16), default="user", nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    coin_balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    account_holder_name: Mapped[str | None] = mapped_column(String(120))
    bank_account_number: Mapped[str | None] = mapped_column(String(40))
    ifsc_code: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    coin_transactions: Mapped[list["CoinTransaction"]] = relationship(
        back_populates="user", foreign_keys="CoinTransaction.user_id"
    )
    credit_requests: Mapped[list["CreditRequest"]] = relationship(
        back_populates="user", foreign_keys="CreditRequest.user_id"
    )
    withdrawal_requests: Mapped[list["WithdrawalRequest"]] = relationship(
        back_populates="user", foreign_keys="WithdrawalRequest.user_id"
    )
    verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class CreditRequest(Base):
    __tablename__ = "credit_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_name: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(12), default="PENDING", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    user: Mapped[User] = relationship(back_populates="credit_requests", foreign_keys=[user_id])


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_name: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    account_holder_name: Mapped[str] = mapped_column(String(120), nullable=False)
    bank_account_number: Mapped[str] = mapped_column(String(40), nullable=False)
    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(12), default="PENDING", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    user: Mapped[User] = relationship(back_populates="withdrawal_requests", foreign_keys=[user_id])


class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    __table_args__ = (
        CheckConstraint("amount_delta != 0", name="ck_coin_transactions_nonzero_delta"),
        CheckConstraint("balance_after >= 0", name="ck_coin_transactions_nonnegative_balance"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    amount_delta: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    market: Mapped[str | None] = mapped_column(String(80))
    selection: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user: Mapped[User] = relationship(
        back_populates="coin_transactions", foreign_keys=[user_id]
    )


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="verification_tokens")


class GameMarket(Base):
    __tablename__ = "game_markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
    active_days: Mapped[str] = mapped_column(String(32), default="0,1,2,3,4,5,6", nullable=False)
    bet_cutoff_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class GameRound(Base):
    __tablename__ = "game_rounds"
    __table_args__ = (
        UniqueConstraint("market_id", "round_date", name="uq_game_round_market_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_id: Mapped[int] = mapped_column(
        ForeignKey("game_markets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_panna: Mapped[str | None] = mapped_column(String(3))
    open_digit: Mapped[int | None] = mapped_column(Integer)
    close_panna: Mapped[str | None] = mapped_column(String(3))
    close_digit: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default="scheduled", nullable=False)
    rng_seed_commitment: Mapped[str | None] = mapped_column(String(64))
    rng_seed: Mapped[str | None] = mapped_column(String(64))


class Panna(Base):
    __tablename__ = "game_pannas"

    panna: Mapped[str] = mapped_column(String(3), primary_key=True)
    type: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    digit: Mapped[int] = mapped_column(Integer, nullable=False)


class GameBetType(Base):
    __tablename__ = "game_bet_types"

    code: Mapped[str] = mapped_column(String(24), primary_key=True)
    label: Mapped[str] = mapped_column(String(40), nullable=False)
    win_per_10: Mapped[int] = mapped_column(Integer, nullable=False)
    min_points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_points: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class GameBet(Base):
    __tablename__ = "game_bets"
    __table_args__ = (
        CheckConstraint("points > 0", name="ck_game_bets_positive_points"),
        UniqueConstraint("idempotency_key", name="uq_game_bets_idempotency"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_id: Mapped[int] = mapped_column(
        ForeignKey("game_rounds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bet_type: Mapped[str] = mapped_column(
        ForeignKey("game_bet_types.code"), nullable=False
    )
    session: Mapped[str] = mapped_column(String(8), nullable=False)
    selection: Mapped[str] = mapped_column(String(16), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    win_per_10_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(12), default="pending", nullable=False)
    win_points: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
