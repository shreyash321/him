from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import AliasChoices, BaseModel, Field, field_validator
from sqlalchemy import desc, select

from app.auth import (
    USERNAME_PATTERN,
    _require_same_origin,
    current_user,
    normalize_phone,
    require_csrf,
)
from app.database import SessionFactory
from app.models import (
    CoinTransaction,
    CreditRequest as CreditRequestRecord,
    User,
    WithdrawalRequest as WithdrawalRequestRecord,
)


router = APIRouter(tags=["wallet"])
MAX_COIN_AMOUNT = 1_000_000
MIN_CREDIT_REQUEST = 500
MIN_WITHDRAWAL_REQUEST = 1_000
STATUS_PRIORITY = {"PENDING": 0, "APPROVED": 1, "REJECTED": 2}


class AdminCoinAdjustmentRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    phone: str = Field(min_length=10, max_length=24)
    amount: int = Field(ge=1, le=MAX_COIN_AMOUNT)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not USERNAME_PATTERN.fullmatch(normalized):
            raise ValueError("Enter a valid username.")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)


class BetRequest(BaseModel):
    market: str = Field(min_length=1, max_length=80)
    selection: str = Field(min_length=1, max_length=80)
    amount: int = Field(ge=1, le=MAX_COIN_AMOUNT)

    @field_validator("market", "selection")
    @classmethod
    def clean_text(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("This field cannot be blank.")
        return cleaned


class CreditRequestCreate(BaseModel):
    amount: int = Field(ge=MIN_CREDIT_REQUEST, le=MAX_COIN_AMOUNT)


class WithdrawalRequestCreate(BaseModel):
    amount: int = Field(ge=MIN_WITHDRAWAL_REQUEST, le=MAX_COIN_AMOUNT)
    account_holder_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("account_holder_name", "accountHolderName"),
    )
    bank_account_number: str | None = Field(
        default=None,
        validation_alias=AliasChoices("bank_account_number", "bankAccountNumber"),
    )
    ifsc_code: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ifsc_code", "ifscCode"),
    )

    @field_validator("account_holder_name", "bank_account_number", "ifsc_code")
    @classmethod
    def normalize_bank_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None


async def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    if user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Change the bootstrap password before using admin functions.",
        )
    return user


async def _resolve_bank_profile(user: User, payload: WithdrawalRequestCreate) -> tuple[str, str, str]:
    account_holder_name = (
        (payload.account_holder_name or "").strip()
        or (user.account_holder_name or "").strip()
    )
    bank_account_number = (
        (payload.bank_account_number or "").strip()
        or (user.bank_account_number or "").strip()
    )
    ifsc_code = (payload.ifsc_code or "").strip() or (user.ifsc_code or "").strip()

    if not account_holder_name or not bank_account_number or not ifsc_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please save your bank details before requesting a withdrawal.",
        )
    return account_holder_name, bank_account_number, ifsc_code.upper()


@router.get("/wallet/history")
async def wallet_history(user: User = Depends(current_user)):
    async with SessionFactory() as session:
        transactions = await session.scalars(
            select(CoinTransaction)
            .where(CoinTransaction.user_id == user.id)
            .order_by(desc(CoinTransaction.created_at))
        )
        history = [
            {
                "kind": item.kind,
                "amount_delta": item.amount_delta,
                "balance_after": item.balance_after,
                "description": item.description,
                "market": item.market,
                "selection": item.selection,
                "created_at": item.created_at.isoformat(),
            }
            for item in transactions
        ]
    return {
        "username": user.username,
        "phone": user.phone,
        "coin_balance": user.coin_balance,
        "transactions": history,
        "coins_are_redeemable": False,
    }


@router.post("/api/requests/credit", status_code=status.HTTP_201_CREATED)
async def create_credit_request(
    data: CreditRequestCreate,
    request: Request,
    user: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    async with SessionFactory() as session:
        async with session.begin():
            request_record = CreditRequestRecord(
                user_id=user.id,
                user_name=user.username or user.phone or "User",
                amount=data.amount,
                status="PENDING",
            )
            session.add(request_record)
            await session.flush()
            return {
                "id": request_record.id,
                "type": "credit",
                "user_id": user.id,
                "user_name": request_record.user_name,
                "amount": request_record.amount,
                "status": request_record.status,
                "timestamp": request_record.created_at.isoformat(),
            }


@router.post("/api/requests/withdraw", status_code=status.HTTP_201_CREATED)
async def create_withdrawal_request(
    data: WithdrawalRequestCreate,
    request: Request,
    user: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)

    if user.coin_balance < data.amount:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You do not have enough wallet balance for this withdrawal request.",
        )

    account_holder_name, bank_account_number, ifsc_code = await _resolve_bank_profile(user, data)

    async with SessionFactory() as session:
        async with session.begin():
            saved_user = await session.get(User, user.id, with_for_update=True)
            if saved_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")
            saved_user.account_holder_name = account_holder_name
            saved_user.bank_account_number = bank_account_number
            saved_user.ifsc_code = ifsc_code

            request_record = WithdrawalRequestRecord(
                user_id=saved_user.id,
                user_name=saved_user.username or saved_user.phone or "User",
                amount=data.amount,
                account_holder_name=account_holder_name,
                bank_account_number=bank_account_number,
                ifsc_code=ifsc_code,
                status="PENDING",
            )
            session.add(request_record)
            await session.flush()
            return {
                "id": request_record.id,
                "type": "withdrawal",
                "user_id": saved_user.id,
                "user_name": request_record.user_name,
                "amount": request_record.amount,
                "status": request_record.status,
                "account_holder_name": request_record.account_holder_name,
                "bank_account_number": request_record.bank_account_number,
                "ifsc_code": request_record.ifsc_code,
                "timestamp": request_record.created_at.isoformat(),
            }


@router.get("/api/admin/requests")
async def list_admin_requests(
    request_type: str | None = Query(default=None, alias="type"),
    search: str | None = None,
    username: str | None = None,
    admin: User = Depends(require_admin),
):
    del admin
    async with SessionFactory() as session:
        credit_requests = await session.scalars(
            select(CreditRequestRecord).order_by(desc(CreditRequestRecord.created_at))
        )
        withdrawal_requests = await session.scalars(
            select(WithdrawalRequestRecord).order_by(desc(WithdrawalRequestRecord.created_at))
        )

    records = []
    for item in credit_requests:
        user = await _load_request_user(item.user_id)
        records.append(
            {
                "id": item.id,
                "type": "credit",
                "user_id": item.user_id,
                "user_name": item.user_name,
                "amount": item.amount,
                "requested_amount": item.amount,
                "current_wallet_balance": user.coin_balance if user else 0,
                "status": item.status,
                "timestamp": item.created_at.isoformat(),
                "created_at": item.created_at.isoformat(),
            }
        )
    for item in withdrawal_requests:
        user = await _load_request_user(item.user_id)
        records.append(
            {
                "id": item.id,
                "type": "withdrawal",
                "user_id": item.user_id,
                "user_name": item.user_name,
                "amount": item.amount,
                "requested_amount": item.amount,
                "current_wallet_balance": user.coin_balance if user else 0,
                "status": item.status,
                "account_holder_name": item.account_holder_name,
                "bank_account_number": item.bank_account_number,
                "ifsc_code": item.ifsc_code,
                "timestamp": item.created_at.isoformat(),
                "created_at": item.created_at.isoformat(),
            }
        )

    if request_type:
        request_type = request_type.lower()
        if request_type not in {"all", "credit", "withdraw", "withdrawal"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request type must be 'all', 'credit', or 'withdraw'.",
            )
        if request_type != "all":
            alias = "withdrawal" if request_type in {"withdraw", "withdrawal"} else "credit"
            records = [item for item in records if item["type"] == alias]

    needle = (search or username or "").strip().lower()
    if needle:
        records = [
            item for item in records if needle in (item.get("user_name") or "").lower()
        ]

    records.sort(
        key=lambda item: (
            STATUS_PRIORITY.get(item.get("status", "PENDING"), 99),
            item.get("created_at", ""),
        )
    )
    return {"items": records}


async def _load_request_user(user_id: str) -> User | None:
    async with SessionFactory() as session:
        return await session.get(User, user_id)


@router.post("/api/admin/requests/{request_id}/approve")
async def approve_request(
    request_id: str,
    request: Request,
    admin: User = Depends(require_admin),
):
    _require_same_origin(request)
    await require_csrf(request)
    async with SessionFactory() as session:
        async with session.begin():
            credit_request = await session.get(CreditRequestRecord, request_id)
            withdrawal_request = await session.get(WithdrawalRequestRecord, request_id)
            if credit_request is None and withdrawal_request is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")
            if credit_request is not None:
                request_row = credit_request
                kind = "credit"
            else:
                request_row = withdrawal_request
                kind = "withdrawal"
            if request_row.status != "PENDING":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Only pending requests can be approved.",
                )
            target = await session.get(User, request_row.user_id, with_for_update=True)
            if target is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User no longer exists.")
            if kind == "credit":
                target.coin_balance += request_row.amount
                transaction = CoinTransaction(
                    user_id=target.id,
                    actor_user_id=admin.id,
                    kind="credit_request_approved",
                    amount_delta=request_row.amount,
                    balance_after=target.coin_balance,
                    description="Approved credit request.",
                )
                session.add(transaction)
            else:
                if target.coin_balance < request_row.amount:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This withdrawal cannot be approved because the balance is insufficient.",
                    )
                target.coin_balance -= request_row.amount
                transaction = CoinTransaction(
                    user_id=target.id,
                    actor_user_id=admin.id,
                    kind="withdrawal_request_approved",
                    amount_delta=-request_row.amount,
                    balance_after=target.coin_balance,
                    description="Approved withdrawal request.",
                )
                session.add(transaction)
            request_row.status = "APPROVED"
            request_row.reviewed_at = datetime.now(timezone.utc)
            request_row.reviewed_by_user_id = admin.id
            await session.flush()
            return {
                "id": request_row.id,
                "type": kind,
                "status": request_row.status,
                "amount": request_row.amount,
                "wallet_balance": target.coin_balance,
            }


@router.post("/api/admin/requests/{request_id}/reject")
async def reject_request(
    request_id: str,
    request: Request,
    admin: User = Depends(require_admin),
):
    _require_same_origin(request)
    await require_csrf(request)
    async with SessionFactory() as session:
        async with session.begin():
            credit_request = await session.get(CreditRequestRecord, request_id)
            withdrawal_request = await session.get(WithdrawalRequestRecord, request_id)
            if credit_request is None and withdrawal_request is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")
            if credit_request is not None:
                request_row = credit_request
                kind = "credit"
            else:
                request_row = withdrawal_request
                kind = "withdrawal"
            if request_row.status != "PENDING":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Only pending requests can be rejected.",
                )
            request_row.status = "REJECTED"
            request_row.reviewed_at = datetime.now(timezone.utc)
            request_row.reviewed_by_user_id = admin.id
            await session.flush()
            return {
                "id": request_row.id,
                "type": kind,
                "status": request_row.status,
                "amount": request_row.amount,
            }


@router.post("/wallet/bets", status_code=status.HTTP_201_CREATED)
async def place_virtual_bet(
    data: BetRequest,
    request: Request,
    user: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    async with SessionFactory() as session:
        async with session.begin():
            saved_user = await session.get(User, user.id, with_for_update=True)
            if saved_user is None:
                raise HTTPException(status_code=401, detail="Please log in.")
            if saved_user.coin_balance < data.amount:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You do not have enough virtual coins.",
                )
            saved_user.coin_balance -= data.amount
            transaction = CoinTransaction(
                user_id=saved_user.id,
                kind="bet_debit",
                amount_delta=-data.amount,
                balance_after=saved_user.coin_balance,
                description=f"Virtual bet on {data.market}: {data.selection}",
                market=data.market,
                selection=data.selection,
            )
            session.add(transaction)
            await session.flush()
            result = {
                "transaction_id": transaction.id,
                "coin_balance": saved_user.coin_balance,
                "message": "Virtual bet recorded. It has no cash value or payout.",
            }
    return result


@router.post("/admin/credits", status_code=status.HTTP_201_CREATED)
async def credit_user(
    data: AdminCoinAdjustmentRequest,
    request: Request,
    admin: User = Depends(require_admin),
):
    _require_same_origin(request)
    await require_csrf(request)
    async with SessionFactory() as session:
        async with session.begin():
            target = await session.scalar(
                select(User)
                .where(
                    User.username == data.username,
                    User.phone == data.phone,
                    User.role == "user",
                )
                .with_for_update()
            )
            if target is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No user matches both that username and phone number.",
                )
            target.coin_balance += data.amount
            transaction = CoinTransaction(
                user_id=target.id,
                actor_user_id=admin.id,
                kind="admin_credit",
                amount_delta=data.amount,
                balance_after=target.coin_balance,
                description=f"Virtual coins credited by admin {admin.username}.",
            )
            session.add(transaction)
            await session.flush()
            result = {
                "username": target.username,
                "coin_balance": target.coin_balance,
                "amount_added": data.amount,
                "transaction_id": transaction.id,
            }
    return result


@router.post("/admin/debits", status_code=status.HTTP_201_CREATED)
async def debit_user(
    data: AdminCoinAdjustmentRequest,
    request: Request,
    admin: User = Depends(require_admin),
):
    _require_same_origin(request)
    await require_csrf(request)
    async with SessionFactory() as session:
        async with session.begin():
            target = await session.scalar(
                select(User)
                .where(
                    User.username == data.username,
                    User.phone == data.phone,
                    User.role == "user",
                )
                .with_for_update()
            )
            if target is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No user matches both that username and phone number.",
                )
            if target.coin_balance < data.amount:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The user does not have enough virtual coins for this debit.",
                )
            target.coin_balance -= data.amount
            transaction = CoinTransaction(
                user_id=target.id,
                actor_user_id=admin.id,
                kind="admin_debit",
                amount_delta=-data.amount,
                balance_after=target.coin_balance,
                description=f"Virtual coins debited by admin {admin.username}.",
            )
            session.add(transaction)
            await session.flush()
            result = {
                "username": target.username,
                "coin_balance": target.coin_balance,
                "amount_removed": data.amount,
                "transaction_id": transaction.id,
            }
    return result
