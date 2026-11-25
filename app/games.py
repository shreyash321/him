import asyncio
from datetime import date, datetime, time, timedelta
import hashlib
import logging
import secrets
from typing import Literal
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError

from app.auth import _require_same_origin, current_user, require_csrf
from app.database import SessionFactory
from app.game_rules import bet_matches, calculate_payout, panna_rows
from app.models import CoinTransaction, GameBet, GameBetType, GameMarket, GameRound, Panna, User
from app.config import settings


router = APIRouter(prefix="/api", tags=["virtual games"])
LOCAL_ZONE = ZoneInfo("Asia/Kolkata")
ROUND_EXPOSURE_LIMIT = 5000
logger = logging.getLogger(__name__)
BET_TYPE_MAP = {
    "SINGLE_DIGIT": "single_digit",
    "JODI": "jodi",
    "SINGLE_PANNA": "single_panna",
    "DOUBLE_PANNA": "double_panna",
    "TRIPLE_PANNA": "triple_panna",
}


class BetRequest(BaseModel):
    round_id: int = Field(gt=0)
    bet_type: str
    session: Literal["open", "close", "both"] | None = None
    selection: str = Field(min_length=1, max_length=16)
    points: int = Field(gt=0, le=1_000_000)
    idempotency_key: str = Field(min_length=8, max_length=80)

    @field_validator("bet_type", "selection", "idempotency_key")
    @classmethod
    def trim_fields(cls, value: str) -> str:
        return value.strip()


class ResultRequest(BaseModel):
    session: Literal["open", "close"]
    panna: str = Field(pattern=r"^\d{3}$")


class BetTypeUpdate(BaseModel):
    win_per_10: int = Field(ge=1, le=1_000_000)
    min_points: int = Field(ge=1, le=1_000_000)
    max_points: int = Field(ge=1, le=1_000_000)
    enabled: bool = True


class MarketUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    open_time: time
    close_time: time
    active_days: list[int] = Field(min_length=1, max_length=7)
    bet_cutoff_minutes: int = Field(ge=1, le=180)
    paused: bool
    sort_order: int = Field(ge=0, le=10000)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Market name cannot be blank.")
        return normalized

    @field_validator("active_days")
    @classmethod
    def valid_days(cls, value: list[int]) -> list[int]:
        if any(day < 0 or day > 6 for day in value):
            raise ValueError("Active weekdays must be between 0 and 6.")
        if len(set(value)) != len(value):
            raise ValueError("Active weekdays cannot be repeated.")
        return value


def _now() -> datetime:
    return datetime.now(LOCAL_ZONE)


def _round_cutoff(market: GameMarket, round_date: date, session: str) -> datetime:
    at = market.open_time if session == "open" else market.close_time
    return datetime.combine(round_date, at, LOCAL_ZONE) - timedelta(
        minutes=market.bet_cutoff_minutes
    )


def _market_state(market: GameMarket, round_: GameRound | None, now: datetime) -> dict:
    round_date = round_.round_date if round_ is not None else now.date()
    active = round_date.weekday() in {
        int(day) for day in market.active_days.split(",") if day.strip().isdigit()
    }
    open_cutoff = _round_cutoff(market, round_date, "open")
    close_cutoff = _round_cutoff(market, round_date, "close")
    open_declared = round_ is not None and round_.open_panna is not None
    if market.paused or not active:
        state, session = "CLOSED", None
    elif now < open_cutoff:
        state, session = "RUNNING", "Open + Close betting"
    elif open_declared and now < close_cutoff:
        state, session = "RUNNING", "Close betting only"
    else:
        state, session = "CLOSED", None
    next_cutoff = (
        open_cutoff
        if now < open_cutoff
        else close_cutoff
        if state == "RUNNING"
        else None
    )
    return {
        "status": state,
        "betting_session": session,
        "next_cutoff": next_cutoff.isoformat() if next_cutoff else None,
    }


async def _get_or_create_round(session, market: GameMarket, round_date: date) -> GameRound:
    seed = secrets.token_hex(32)
    dialect = session.get_bind().dialect.name
    insert_round = (
        sqlite_insert(GameRound)
        if dialect == "sqlite"
        else postgresql_insert(GameRound)
    )
    await session.execute(
        insert_round
        .values(
            market_id=market.id,
            round_date=round_date,
            rng_seed=seed,
            rng_seed_commitment=hashlib.sha256(seed.encode("ascii")).hexdigest(),
        )
        .on_conflict_do_nothing(index_elements=["market_id", "round_date"])
    )
    round_ = await session.scalar(
        select(GameRound).where(
            GameRound.market_id == market.id, GameRound.round_date == round_date
        )
    )
    if round_ is None:
        raise RuntimeError("The market round could not be created.")
    return round_


def _rng_panna(seed: str, session_name: str) -> str:
    rows = panna_rows()
    digest = hashlib.sha256(f"{seed}:{session_name}".encode("ascii")).digest()
    return rows[int.from_bytes(digest, "big") % len(rows)][0]


async def _settle_pending_bets(
    session, round_: GameRound, declared_session: str, actor_user_id: str | None
) -> int:
    market = await session.get(GameMarket, round_.market_id)
    if market is None:
        raise RuntimeError("The market for this round no longer exists.")
    pending = await session.scalars(
        select(GameBet)
        .where(GameBet.round_id == round_.id, GameBet.status == "pending")
        .with_for_update()
    )
    settled = 0
    for bet in pending:
        if declared_session == "open" and (
            bet.session != "open" or bet.bet_type == "JODI"
        ):
            continue
        if declared_session == "close" and bet.session == "open":
            continue
        won = _bet_won(bet, round_, declared_session)
        bet.status = "won" if won else "lost"
        bet.settled_at = _now()
        if won:
            bet.win_points = calculate_payout(bet.points, bet.win_per_10_snapshot)
            player = await session.get(User, bet.user_id, with_for_update=True)
            if player is None:
                raise RuntimeError("A pending entry owner no longer exists.")
            player.coin_balance += bet.win_points
            session.add(
                CoinTransaction(
                    user_id=player.id,
                    actor_user_id=actor_user_id,
                    kind="bet_payout",
                    amount_delta=bet.win_points,
                    balance_after=player.coin_balance,
                    description=f"Virtual points result: {bet.bet_type}",
                    market=market.name,
                    selection=bet.selection,
                )
            )
        settled += 1
    return settled


async def game_scheduler_tick(now: datetime | None = None) -> None:
    if settings.result_mode != "rng":
        return
    current = now or _now()
    today = current.date()
    async with SessionFactory() as session:
        async with session.begin():
            markets = await session.scalars(
                select(GameMarket).where(GameMarket.paused.is_(False))
            )
            for market in markets:
                if today.weekday() not in {
                    int(day)
                    for day in market.active_days.split(",")
                    if day.strip().isdigit()
                }:
                    continue
                round_ = await _get_or_create_round(session, market, today)
                if not round_.rng_seed or not round_.rng_seed_commitment:
                    seed = secrets.token_hex(32)
                    round_.rng_seed = seed
                    round_.rng_seed_commitment = hashlib.sha256(
                        seed.encode("ascii")
                    ).hexdigest()
                if (
                    round_.open_panna is None
                    and current >= _round_cutoff(market, today, "open")
                ):
                    panna = await session.get(Panna, _rng_panna(round_.rng_seed, "open"))
                    if panna is None:
                        raise RuntimeError("The selected RNG result is missing from the panna table.")
                    round_.open_panna = panna.panna
                    round_.open_digit = panna.digit
                    round_.status = "open_declared"
                    await _settle_pending_bets(session, round_, "open", None)
                if (
                    round_.close_panna is None
                    and round_.open_panna is not None
                    and current >= _round_cutoff(market, today, "close")
                ):
                    panna = await session.get(Panna, _rng_panna(round_.rng_seed, "close"))
                    if panna is None:
                        raise RuntimeError("The selected RNG result is missing from the panna table.")
                    round_.close_panna = panna.panna
                    round_.close_digit = panna.digit
                    round_.status = "completed"
                    await _settle_pending_bets(session, round_, "close", None)


async def game_scheduler_loop() -> None:
    while True:
        try:
            await game_scheduler_tick()
        except Exception:
            logger.exception("Could not reconcile virtual game rounds.")
        await asyncio.sleep(15)


def _round_payload(market: GameMarket, round_: GameRound, now: datetime) -> dict:
    state = _market_state(market, round_, now)
    open_cutoff = _round_cutoff(market, round_.round_date, "open")
    close_cutoff = _round_cutoff(market, round_.round_date, "close")
    active = round_.round_date.weekday() in {
        int(day) for day in market.active_days.split(",") if day.strip().isdigit()
    }
    return {
        "round_id": round_.id,
        "date": round_.round_date.isoformat(),
        **state,
        "open_cutoff": open_cutoff.isoformat(),
        "close_cutoff": close_cutoff.isoformat(),
        "open_betting": active and not market.paused and now < open_cutoff,
        "close_betting": active
        and not market.paused
        and (
            now < open_cutoff
            or round_.open_panna is not None and now < close_cutoff
        ),
        "jodi_betting": active and not market.paused and now < open_cutoff,
        "running": state["status"] == "RUNNING",
        "open_panna": round_.open_panna,
        "open_digit": round_.open_digit,
        "close_panna": round_.close_panna,
        "close_digit": round_.close_digit,
        "result_commitment": round_.rng_seed_commitment,
        "jodi": (
            f"{round_.open_digit}{round_.close_digit}"
            if round_.open_digit is not None and round_.close_digit is not None
            else None
        ),
    }


@router.get("/markets")
async def list_markets():
    now = _now()
    async with SessionFactory() as session:
        markets = list(
            await session.scalars(
                select(GameMarket).order_by(GameMarket.sort_order, GameMarket.name)
            )
        )
        all_rounds = list(
            await session.scalars(
                select(GameRound).order_by(GameRound.round_date.desc())
            )
        )
        rounds = {}
        for round_ in all_rounds:
            if round_.market_id not in rounds and (
                round_.open_panna is not None or round_.close_panna is not None
            ):
                rounds[round_.market_id] = round_
        today_rounds = {
            round_.market_id: round_
            for round_ in all_rounds
            if round_.round_date == now.date()
        }
        result = [
            {
                "id": market.id,
                "name": market.name,
                "open_time": market.open_time.strftime("%I:%M %p"),
                "close_time": market.close_time.strftime("%I:%M %p"),
                "open_time_24": market.open_time.strftime("%H:%M"),
                "close_time_24": market.close_time.strftime("%H:%M"),
                "active_days": market.active_days,
                "bet_cutoff_minutes": market.bet_cutoff_minutes,
                "paused": market.paused,
                "sort_order": market.sort_order,
                "latest_result": (
                    f"{round_.open_panna or '***'}-"
                    f"{f'{round_.open_digit}{round_.close_digit}' if round_.close_digit is not None else '**'}-"
                    f"{round_.close_panna or '***'}"
                    if round_ and (round_.open_panna or round_.close_panna)
                    else "***-**"
                ),
                **_market_state(market, today_rounds.get(market.id), now),
            }
            for market in markets
        ]
        result.sort(
            key=lambda item: (
                item["status"] != "RUNNING",
                item["next_cutoff"] or "9999",
                item["name"],
            )
        )
        return result


@router.get("/markets/{market_id}/today")
async def get_market_round(market_id: int, round_date: date | None = None):
    now = _now()
    day = round_date or now.date()
    if day < now.date() or day > now.date() + timedelta(days=7):
        raise HTTPException(status_code=422, detail="Choose today or a date within 7 days.")
    async with SessionFactory() as session:
        async with session.begin():
            market = await session.get(GameMarket, market_id)
            if market is None:
                raise HTTPException(status_code=404, detail="Market not found.")
            if day.weekday() not in {
                int(item) for item in market.active_days.split(",") if item.strip().isdigit()
            }:
                raise HTTPException(status_code=404, detail="This market has no round on that date.")
            round_ = await _get_or_create_round(session, market, day)
            result = _round_payload(market, round_, now)
        result.update(
            {
                "market_id": market.id,
                "market": market.name,
                "open_time": market.open_time.strftime("%I:%M %p"),
                "close_time": market.close_time.strftime("%I:%M %p"),
                "bet_cutoff_minutes": market.bet_cutoff_minutes,
            }
        )
        return result


@router.get("/bet-types")
async def list_bet_types(include_disabled: bool = False):
    async with SessionFactory() as session:
        query = select(GameBetType).order_by(GameBetType.code)
        if not include_disabled:
            query = query.where(GameBetType.enabled.is_(True))
        types = await session.scalars(query)
        return [
            {
                "code": item.code,
                "label": item.label,
                "win_per_10": item.win_per_10,
                "multiplier": item.win_per_10 / 10,
                "min_points": item.min_points,
                "max_points": item.max_points,
                "enabled": item.enabled,
            }
            for item in types
        ]


@router.get("/panna/suggest")
async def suggest_panna(type: Literal["single", "double", "triple"], prefix: str = ""):
    if len(prefix) > 3 or not prefix.isdigit() and prefix:
        raise HTTPException(status_code=422, detail="Panna prefix must contain digits only.")
    async with SessionFactory() as session:
        pannas = await session.scalars(
            select(Panna.panna)
            .where(Panna.type == type, Panna.panna.startswith(prefix))
            .order_by(Panna.panna)
            .limit(30)
        )
        return {"suggestions": list(pannas)}


def _validate_selection(code: str, selection: str, session_value: str | None) -> str:
    if code == "SINGLE_DIGIT":
        if len(selection) != 1 or selection not in "0123456789":
            raise HTTPException(status_code=422, detail="Enter one digit from 0 to 9.")
        if session_value not in {"open", "close"}:
            raise HTTPException(status_code=422, detail="Choose an Open or Close session.")
        return session_value
    if code == "JODI":
        if len(selection) != 2 or not selection.isdigit():
            raise HTTPException(status_code=422, detail="Enter a two-digit Jodi from 00 to 99.")
        if session_value not in {None, "both"}:
            raise HTTPException(status_code=422, detail="Jodi bets do not use a session.")
        return "both"
    if code in {"SINGLE_PANNA", "DOUBLE_PANNA", "TRIPLE_PANNA"}:
        if len(selection) != 3 or not selection.isdigit():
            raise HTTPException(status_code=422, detail="Enter a three-digit panna.")
        if session_value not in {"open", "close"}:
            raise HTTPException(status_code=422, detail="Choose an Open or Close session.")
        return session_value
    raise HTTPException(status_code=422, detail="This game type is not available.")


@router.post("/bets", status_code=status.HTTP_201_CREATED)
async def place_bet(
    data: BetRequest,
    request: Request,
    user: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if user.role != "user":
        raise HTTPException(status_code=403, detail="Only player accounts can place entries.")
    try:
        redis = request.app.state.auth_redis
        key = f"game:bets:rate:{user.id}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Bet service is temporarily unavailable.",
            headers={"Retry-After": "5"},
        ) from error
    if count > 30:
        raise HTTPException(
            status_code=429,
            detail="Too many entries. Try again in a minute.",
            headers={"Retry-After": "60"},
        )
    now = _now()
    async with SessionFactory() as session:
        async with session.begin():
            previous = await session.scalar(
                select(GameBet).where(GameBet.idempotency_key == data.idempotency_key)
            )
            if previous is not None:
                if previous.user_id != user.id:
                    raise HTTPException(status_code=409, detail="Idempotency key already used.")
                saved_user = await session.get(User, user.id)
                return {
                    "id": previous.id,
                    "status": previous.status,
                    "points": previous.points,
                    "coin_balance": saved_user.coin_balance,
                    "duplicate": True,
                }
            round_ = await session.scalar(
                select(GameRound).where(GameRound.id == data.round_id).with_for_update()
            )
            if round_ is None:
                raise HTTPException(status_code=404, detail="Round not found.")
            previous = await session.scalar(
                select(GameBet).where(GameBet.idempotency_key == data.idempotency_key)
            )
            if previous is not None:
                if previous.user_id != user.id:
                    raise HTTPException(status_code=409, detail="Idempotency key already used.")
                saved_user = await session.get(User, user.id)
                return {
                    "id": previous.id,
                    "status": previous.status,
                    "points": previous.points,
                    "coin_balance": saved_user.coin_balance,
                    "duplicate": True,
                }
            market = await session.get(GameMarket, round_.market_id)
            bet_type = await session.get(GameBetType, data.bet_type)
            if market is None or bet_type is None or not bet_type.enabled:
                raise HTTPException(status_code=422, detail="Game type or market is unavailable.")
            if (
                market.paused
                or round_.round_date < now.date()
                or round_.round_date > now.date() + timedelta(days=7)
                or round_.round_date.weekday()
                not in {
                    int(day)
                    for day in market.active_days.split(",")
                    if day.strip().isdigit()
                }
            ):
                raise HTTPException(status_code=409, detail="This market round is not accepting entries.")
            session_value = _validate_selection(data.bet_type, data.selection, data.session)
            if data.points < bet_type.min_points or data.points > bet_type.max_points:
                raise HTTPException(
                    status_code=422,
                    detail=f"Points must be between {bet_type.min_points} and {bet_type.max_points}.",
                )
            if data.bet_type.endswith("_PANNA"):
                panna_type = BET_TYPE_MAP[data.bet_type]
                valid = await session.scalar(
                    select(Panna.panna).where(
                        Panna.panna == data.selection, Panna.type == panna_type
                    )
                )
                if valid is None:
                    raise HTTPException(status_code=422, detail="Invalid panna for this game.")
            uses_open_cutoff = data.bet_type == "JODI" or session_value == "open"
            cutoff_session = "open" if uses_open_cutoff else "close"
            cutoff = _round_cutoff(market, round_.round_date, cutoff_session)
            if now >= cutoff:
                raise HTTPException(status_code=409, detail="Betting closed for this session.")
            if (
                session_value == "close"
                and round_.open_panna is None
                and now >= _round_cutoff(market, round_.round_date, "open")
            ):
                raise HTTPException(
                    status_code=409, detail="Close betting opens after the Open result."
                )
            staked = await session.scalar(
                select(func.coalesce(func.sum(GameBet.points), 0)).where(
                    GameBet.round_id == round_.id,
                    GameBet.user_id == user.id,
                )
            )
            if staked + data.points > ROUND_EXPOSURE_LIMIT:
                raise HTTPException(status_code=409, detail="Round points limit exceeded.")
            saved_user = await session.get(User, user.id, with_for_update=True)
            if saved_user is None:
                raise HTTPException(status_code=401, detail="Please log in.")
            if saved_user.coin_balance < data.points:
                raise HTTPException(
                    status_code=409,
                    detail=f"Should be less than wallet balance {saved_user.coin_balance}",
                )
            bet = GameBet(
                id=str(uuid4()),
                user_id=saved_user.id,
                round_id=round_.id,
                bet_type=bet_type.code,
                session=session_value,
                selection=data.selection,
                points=data.points,
                win_per_10_snapshot=bet_type.win_per_10,
                idempotency_key=data.idempotency_key,
            )
            saved_user.coin_balance -= data.points
            session.add(
                CoinTransaction(
                    user_id=saved_user.id,
                    kind="bet_debit",
                    amount_delta=-data.points,
                    balance_after=saved_user.coin_balance,
                    description=f"Virtual points entry: {bet_type.label} {data.selection}",
                    market=market.name,
                    selection=data.selection,
                )
            )
            session.add(bet)
            await session.flush()
            return {
                "id": bet.id,
                "status": bet.status,
                "points": bet.points,
                "coin_balance": saved_user.coin_balance,
                "duplicate": False,
            }


@router.get("/bets")
async def my_bets(
    status_filter: Literal["pending", "won", "lost", "refunded", "all"] = Query(
        "all", alias="status"
    ),
    page: int = 1,
    user: User = Depends(current_user),
):
    if page < 1:
        raise HTTPException(status_code=422, detail="Page must be positive.")
    async with SessionFactory() as session:
        query = (
            select(GameBet, GameRound, GameMarket, GameBetType)
            .join(GameRound, GameBet.round_id == GameRound.id)
            .join(GameMarket, GameRound.market_id == GameMarket.id)
            .join(GameBetType, GameBet.bet_type == GameBetType.code)
            .where(GameBet.user_id == user.id)
            .order_by(GameBet.created_at.desc())
            .offset((page - 1) * 50)
            .limit(50)
        )
        if status_filter != "all":
            query = query.where(GameBet.status == status_filter)
        rows = (await session.execute(query)).all()
        return {
            "items": [
                {
                    "id": bet.id,
                    "market": market.name,
                    "date": round_.round_date.isoformat(),
                    "game": game_type.label,
                    "session": bet.session,
                    "selection": bet.selection,
                    "points": bet.points,
                    "status": bet.status,
                    "win_points": bet.win_points,
                    "created_at": bet.created_at.isoformat(),
                }
                for bet, round_, market, game_type in rows
            ],
            "page": page,
        }


@router.post("/admin/rounds/{round_id}/result")
async def declare_result(
    round_id: int,
    data: ResultRequest,
    request: Request,
    admin: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if admin.role != "admin" or admin.must_change_password:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    if settings.result_mode != "admin":
        raise HTTPException(status_code=403, detail="Manual results are disabled in RNG mode.")
    async with SessionFactory() as session:
        async with session.begin():
            round_ = await session.scalar(
                select(GameRound).where(GameRound.id == round_id).with_for_update()
            )
            if round_ is None:
                raise HTTPException(status_code=404, detail="Round not found.")
            existing = round_.open_panna if data.session == "open" else round_.close_panna
            if existing is not None:
                raise HTTPException(status_code=409, detail="This result was already declared.")
            panna = await session.get(Panna, data.panna)
            if panna is None:
                raise HTTPException(status_code=422, detail="Invalid panna.")
            market = await session.get(GameMarket, round_.market_id)
            if market is None:
                raise HTTPException(status_code=404, detail="Market not found.")
            if _now() < _round_cutoff(market, round_.round_date, data.session):
                raise HTTPException(status_code=409, detail="The session cutoff has not passed.")
            if data.session == "close" and round_.open_panna is None:
                raise HTTPException(status_code=409, detail="Declare the Open result first.")
            if data.session == "open":
                round_.open_panna = panna.panna
                round_.open_digit = panna.digit
            else:
                round_.close_panna = panna.panna
                round_.close_digit = panna.digit
            if round_.close_panna is not None:
                round_.status = "completed"
            elif round_.open_panna is not None:
                round_.status = "open_declared"
            settled_count = await _settle_pending_bets(
                session, round_, data.session, admin.id
            )
            return {"round_id": round_.id, "session": data.session, "settled": settled_count}


@router.post("/admin/rounds/{round_id}/cancel")
async def cancel_round(
    round_id: int,
    request: Request,
    admin: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if admin.role != "admin" or admin.must_change_password:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    async with SessionFactory() as session:
        async with session.begin():
            round_ = await session.scalar(
                select(GameRound).where(GameRound.id == round_id).with_for_update()
            )
            if round_ is None:
                raise HTTPException(status_code=404, detail="Round not found.")
            if round_.status == "cancelled":
                return {"round_id": round_.id, "refunded": 0}
            pending = await session.scalars(
                select(GameBet)
                .where(GameBet.round_id == round_.id, GameBet.status == "pending")
                .with_for_update()
            )
            refunded = 0
            for bet in pending:
                player = await session.get(User, bet.user_id, with_for_update=True)
                if player is None:
                    raise HTTPException(status_code=409, detail="Bet owner no longer exists.")
                player.coin_balance += bet.points
                bet.status = "refunded"
                bet.settled_at = _now()
                session.add(
                    CoinTransaction(
                        user_id=player.id,
                        actor_user_id=admin.id,
                        kind="bet_refund",
                        amount_delta=bet.points,
                        balance_after=player.coin_balance,
                        description="Virtual points refunded for cancelled round.",
                    )
                )
                refunded += 1
            round_.status = "cancelled"
            return {"round_id": round_.id, "refunded": refunded}


@router.put("/admin/bet-types/{code}")
async def update_bet_type(
    code: str,
    data: BetTypeUpdate,
    request: Request,
    admin: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if admin.role != "admin" or admin.must_change_password:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    if data.max_points < data.min_points:
        raise HTTPException(status_code=422, detail="Maximum points must be at least the minimum.")
    async with SessionFactory() as session:
        async with session.begin():
            bet_type = await session.get(GameBetType, code, with_for_update=True)
            if bet_type is None:
                raise HTTPException(status_code=404, detail="Game type not found.")
            bet_type.win_per_10 = data.win_per_10
            bet_type.min_points = data.min_points
            bet_type.max_points = data.max_points
            bet_type.enabled = data.enabled
    return {"code": code, **data.model_dump()}


@router.put("/admin/markets/{market_id}")
async def update_market(
    market_id: int,
    data: MarketUpdate,
    request: Request,
    admin: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if admin.role != "admin" or admin.must_change_password:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    if data.close_time <= data.open_time:
        raise HTTPException(status_code=422, detail="Close time must follow open time.")
    async with SessionFactory() as session:
        async with session.begin():
            market = await session.get(GameMarket, market_id, with_for_update=True)
            if market is None:
                raise HTTPException(status_code=404, detail="Market not found.")
            market.name = data.name.strip()
            market.open_time = data.open_time
            market.close_time = data.close_time
            market.active_days = ",".join(str(day) for day in sorted(data.active_days))
            market.bet_cutoff_minutes = data.bet_cutoff_minutes
            market.paused = data.paused
            market.sort_order = data.sort_order
    return {"id": market_id, **data.model_dump()}


@router.post("/admin/markets", status_code=status.HTTP_201_CREATED)
async def create_market(
    data: MarketUpdate,
    request: Request,
    admin: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if admin.role != "admin" or admin.must_change_password:
        raise HTTPException(status_code=403, detail="Administrator access required.")
    if data.close_time <= data.open_time:
        raise HTTPException(status_code=422, detail="Close time must follow open time.")
    try:
        async with SessionFactory() as session:
            async with session.begin():
                market = GameMarket(
                    name=data.name,
                    open_time=data.open_time,
                    close_time=data.close_time,
                    active_days=",".join(str(day) for day in sorted(data.active_days)),
                    bet_cutoff_minutes=data.bet_cutoff_minutes,
                    paused=data.paused,
                    sort_order=data.sort_order,
                )
                session.add(market)
                await session.flush()
                market_id = market.id
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="A market with that name already exists.") from error
    return {"id": market_id, **data.model_dump()}


def _bet_won(bet: GameBet, round_: GameRound, declared_session: str) -> bool:
    return bet_matches(
        code=bet.bet_type,
        selection=bet.selection,
        session=bet.session if bet.bet_type != "JODI" else declared_session,
        open_panna=round_.open_panna,
        open_digit=round_.open_digit,
        close_panna=round_.close_panna,
        close_digit=round_.close_digit,
    )


@router.get("/results/history")
async def results_history(market_id: int | None = None, limit: int = 30):
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="Limit must be between 1 and 100.")
    async with SessionFactory() as session:
        query = (
            select(GameRound, GameMarket)
            .join(GameMarket, GameRound.market_id == GameMarket.id)
            .where(GameRound.open_panna.is_not(None))
            .order_by(GameRound.round_date.desc())
            .limit(limit)
        )
        if market_id is not None:
            query = query.where(GameRound.market_id == market_id)
        rows = (await session.execute(query)).all()
        return [
            {
                "market": market.name,
                "date": round_.round_date.isoformat(),
                "open_panna": round_.open_panna,
                "open_digit": round_.open_digit,
                "jodi": (
                    f"{round_.open_digit}{round_.close_digit}"
                    if round_.close_digit is not None
                    else None
                ),
                "round_id": round_.id,
                "close_panna": round_.close_panna,
                "close_digit": round_.close_digit,
            }
            for round_, market in rows
        ]


@router.get("/verify/{round_id}")
async def verify_round(round_id: int):
    async with SessionFactory() as session:
        round_ = await session.get(GameRound, round_id)
        if round_ is None:
            raise HTTPException(status_code=404, detail="Round not found.")
        revealed = (
            settings.result_mode == "rng"
            and round_.status == "completed"
            and round_.rng_seed is not None
        )
        return {
            "round_id": round_.id,
            "mode": settings.result_mode,
            "commitment": round_.rng_seed_commitment,
            "seed": round_.rng_seed if revealed else None,
            "open_panna": round_.open_panna,
            "close_panna": round_.close_panna,
            "verified": bool(
                revealed
                and hashlib.sha256(round_.rng_seed.encode("ascii")).hexdigest()
                == round_.rng_seed_commitment
                and round_.open_panna == _rng_panna(round_.rng_seed, "open")
                and round_.close_panna == _rng_panna(round_.rng_seed, "close")
            ),
        }


@router.get("/result-mode")
async def get_result_mode():
    return {"mode": settings.result_mode}
