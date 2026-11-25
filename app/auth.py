import hashlib
import hmac
import re
import secrets
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import SessionFactory
from app.models import CoinTransaction, User


router = APIRouter(prefix="/auth", tags=["authentication"])
password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("not-a-real-user-password")
SESSION_COOKIE = "site_session"
CSRF_COOKIE = "site_csrf"
SESSION_TTL_SECONDS = 12 * 60 * 60
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,32}$")
E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_phone(value: str) -> str:
    value = value.strip()
    if not re.fullmatch(r"\+?[\d\s().-]{10,24}", value):
        raise ValueError("Enter a valid phone number.")
    digits = "".join(character for character in value if character.isdigit())
    if value.startswith("+"):
        normalized = f"+{digits}"
    elif len(digits) == 10:
        normalized = f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        normalized = f"+{digits}"
    else:
        raise ValueError("Use a full international number or a 10-digit Indian number.")
    if not E164_PATTERN.fullmatch(normalized):
        raise ValueError("Enter a valid phone number.")
    return normalized


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_]+$")
    phone: str = Field(min_length=10, max_length=24)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not USERNAME_PATTERN.fullmatch(value):
            raise ValueError("Username must be 3-32 letters, numbers, or underscores.")
        return value


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        value = value.strip()
        try:
            return normalize_phone(value)
        except ValueError:
            username = value.lower()
            if not USERNAME_PATTERN.fullmatch(username):
                raise ValueError("Enter a valid phone number or username.")
            return username


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


def _session_key(token: str) -> str:
    digest = hmac.new(
        settings.session_secret.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"auth:session:{digest}"


def _client_key(request: Request) -> str:
    client = request.client.host if request.client else "unknown"
    return hashlib.sha256(client.encode("utf-8")).hexdigest()[:32]


async def _check_rate_limit(
    request: Request,
    action: str,
    *,
    limit: int,
    window_seconds: int,
    identifier: str | None = None,
) -> None:
    redis = request.app.state.auth_redis
    key_parts = [f"auth:rate:{action}", _client_key(request)]
    if identifier is not None:
        hashed_identifier = hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:32]
        key_parts.append(hashed_identifier)
    key = ":".join(key_parts)
    try:
        async with redis.pipeline(transaction=True) as pipeline:
            pipeline.incr(key)
            pipeline.expire(key, window_seconds)
            count, _ = await pipeline.execute()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is temporarily unavailable.",
            headers={"Retry-After": "5"},
        ) from error
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please try again later.",
            headers={"Retry-After": str(window_seconds)},
        )


def _require_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    host = request.headers.get("host")
    if not origin or not host:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin was not accepted.",
        )
    origin_parts = urlsplit(origin)
    if (
        origin_parts.scheme not in {"http", "https"}
        or not origin_parts.netloc
        or origin_parts.path
        or origin_parts.query
        or origin_parts.fragment
        or origin_parts.username
        or origin_parts.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin was not accepted.",
        )

    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    request_scheme = (
        forwarded_proto if forwarded_proto in {"http", "https"} else request.url.scheme
    )
    expected_origin = f"{request_scheme.lower()}://{host.lower()}"
    actual_origin = f"{origin_parts.scheme.lower()}://{origin_parts.netloc.lower()}"
    if not hmac.compare_digest(actual_origin, expected_origin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin was not accepted.",
        )


async def require_csrf(request: Request) -> None:
    session_token = request.cookies.get(SESSION_COOKIE)
    csrf_cookie = request.cookies.get(CSRF_COOKIE)
    csrf_header = request.headers.get("x-csrf-token")
    if not session_token or not csrf_cookie or not csrf_header:
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")
    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")
    try:
        session_value = await request.app.state.auth_redis.get(_session_key(session_token))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is temporarily unavailable.",
        ) from error
    if not session_value:
        raise HTTPException(status_code=403, detail="Login session has expired.")
    try:
        _, stored_csrf = session_value.decode().split(":", 1)
    except (AttributeError, UnicodeDecodeError, ValueError):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")
    if not hmac.compare_digest(stored_csrf, csrf_header):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")


async def _set_session(response: Response, request: Request, user_id: str) -> None:
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    try:
        await request.app.state.auth_redis.set(
            _session_key(session_token),
            f"{user_id}:{csrf_token}",
            ex=SESSION_TTL_SECONDS,
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create a login session.",
            headers={"Retry-After": "5"},
        ) from error

    response.set_cookie(
        SESSION_COOKIE,
        session_token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        max_age=SESSION_TTL_SECONDS,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


async def current_user(request: Request) -> User:
    session_token = request.cookies.get(SESSION_COOKIE)
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")
    try:
        session_value = await request.app.state.auth_redis.get(_session_key(session_token))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is temporarily unavailable.",
        ) from error
    if not session_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")

    try:
        user_id, _ = session_value.decode().split(":", 1)
    except (AttributeError, UnicodeDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")
    async with SessionFactory() as session:
        user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in.")
    return user


async def bootstrap_admin() -> None:
    if not settings.admin_username and not settings.admin_password:
        async with SessionFactory() as session:
            has_admin = await session.scalar(
                select(User.id).where(User.role == "admin").limit(1)
            )
        if has_admin is None:
            raise RuntimeError(
                "Set ADMIN_USERNAME and ADMIN_PASSWORD to bootstrap the first admin."
            )
        return
    if not settings.admin_username or not settings.admin_password:
        raise RuntimeError("Set both ADMIN_USERNAME and ADMIN_PASSWORD to bootstrap an admin.")
    username = settings.admin_username.lower()
    if not USERNAME_PATTERN.fullmatch(username):
        raise RuntimeError("ADMIN_USERNAME must be 3-32 letters, numbers, or underscores.")

    try:
        async with SessionFactory() as session:
            async with session.begin():
                existing = await session.scalar(
                    select(User).where(User.username == username)
                )
                if existing is None:
                    session.add(
                        User(
                            username=username,
                            phone=None,
                            email=None,
                            password_hash=password_hash.hash(settings.admin_password),
                            role="admin",
                            must_change_password=True,
                        )
                    )
                elif existing.role != "admin":
                    raise RuntimeError(
                        "The configured admin username is already used by a non-admin account."
                    )
    except IntegrityError:
        async with SessionFactory() as session:
            existing = await session.scalar(select(User).where(User.username == username))
            if existing is None or existing.role != "admin":
                raise


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, request: Request):
    _require_same_origin(request)
    await _check_rate_limit(request, "register", limit=5, window_seconds=3600)
    async with SessionFactory() as session:
        try:
            async with session.begin():
                user = User(
                    username=data.username,
                    phone=data.phone,
                    email=None,
                    password_hash=password_hash.hash(data.password),
                    coin_balance=0,
                )
                session.add(user)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration failed. This username or phone number may already be in use.",
            )
    return {
        "registered": True,
        "message": "Your account was created successfully. You can now log in.",
    }


@router.post("/login")
async def login(data: LoginRequest, request: Request, response: Response):
    _require_same_origin(request)
    await _check_rate_limit(request, "login", limit=20, window_seconds=900)
    await _check_rate_limit(
        request,
        "login-account",
        limit=5,
        window_seconds=900,
        identifier=data.identifier,
    )
    async with SessionFactory() as session:
        user = await session.scalar(
            select(User).where(
                or_(User.phone == data.identifier, User.username == data.identifier)
            )
        )
        valid_password = password_hash.verify(
            data.password,
            user.password_hash if user is not None else DUMMY_PASSWORD_HASH,
        )
        if user is None or not valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username or phone number and password are incorrect.",
            )
        user_id = user.id
        username = user.username
        role = user.role
        must_change_password = user.must_change_password

    await _set_session(response, request, user_id)
    return {
        "username": username,
        "role": role,
        "must_change_password": must_change_password,
    }


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    request: Request,
    user: User = Depends(current_user),
):
    _require_same_origin(request)
    await require_csrf(request)
    if not password_hash.verify(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    if hmac.compare_digest(data.current_password, data.new_password):
        raise HTTPException(
            status_code=400, detail="Choose a new password different from the current one."
        )

    async with SessionFactory() as session:
        async with session.begin():
            saved_user = await session.get(User, user.id, with_for_update=True)
            if saved_user is None:
                raise HTTPException(status_code=401, detail="Please log in.")
            saved_user.password_hash = password_hash.hash(data.new_password)
            saved_user.must_change_password = False
    return {"message": "Password changed. Your admin account is now ready."}


@router.get("/me")
async def me(user: User = Depends(current_user)):
    return {
        "username": user.username,
        "phone": user.phone,
        "role": user.role,
        "coin_balance": user.coin_balance,
        "must_change_password": user.must_change_password,
        "account_holder_name": user.account_holder_name,
        "bank_account_number": user.bank_account_number,
        "ifsc_code": user.ifsc_code,
    }


@router.post("/logout")
async def logout(request: Request, response: Response):
    _require_same_origin(request)
    await require_csrf(request)
    session_token = request.cookies[SESSION_COOKIE]
    try:
        await request.app.state.auth_redis.delete(_session_key(session_token))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not end the login session.",
        ) from error

    response.delete_cookie(SESSION_COOKIE, path="/", secure=settings.cookie_secure, httponly=True)
    response.delete_cookie(CSRF_COOKIE, path="/", secure=settings.cookie_secure)
    return {"message": "Logged out."}
