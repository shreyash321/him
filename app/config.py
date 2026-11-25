import math
import os
from dataclasses import dataclass
from urllib.parse import urlsplit


def _positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value


def _positive_float(name: str, default: float) -> float:
    value = float(os.getenv(name, str(default)))
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive number.")
    return value


@dataclass(frozen=True)
class Settings:
    environment: str
    public_base_url: str
    session_secret: str
    database_url: str
    redis_url: str
    auth_redis_url: str
    upstream_origin: str
    results_refresh_seconds: int
    page_cache_seconds: int
    asset_cache_seconds: int
    stale_cache_seconds: int
    upstream_requests_per_second: float
    db_pool_size: int
    db_max_overflow: int
    admin_username: str
    admin_password: str
    result_mode: str

    @property
    def production(self) -> bool:
        return self.environment == "production"

    @property
    def cookie_secure(self) -> bool:
        return self.production

    def validate_runtime(self) -> None:
        if self.production and self.public_base_url.startswith("http://"):
            raise ValueError("PUBLIC_BASE_URL must use HTTPS in production.")
        if self.production and len(self.session_secret) < 32:
            raise ValueError("SESSION_SECRET must contain at least 32 characters in production.")
        if self.production and self.admin_username and len(self.admin_password) < 16:
            raise ValueError("Production bootstrap admin password must contain at least 16 characters.")


def load_settings() -> Settings:
    environment = os.getenv("APP_ENV", "development").strip().lower()
    if environment not in {"development", "production", "test"}:
        raise ValueError("APP_ENV must be development, production, or test.")

    public_base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    public_parts = urlsplit(public_base_url)
    if (
        public_parts.scheme not in {"http", "https"}
        or not public_parts.netloc
        or public_parts.path
        or public_parts.query
        or public_parts.fragment
    ):
        raise ValueError("PUBLIC_BASE_URL must be an HTTP(S) origin without a path.")
    session_secret = os.getenv(
        "SESSION_SECRET", "development-only-change-this-secret-before-deploying"
    )

    upstream_origin = os.getenv("UPSTREAM_ORIGIN", "https://matkaonline.games").rstrip("/")
    upstream_parts = urlsplit(upstream_origin)
    if upstream_parts.scheme != "https" or not upstream_parts.netloc:
        raise ValueError("UPSTREAM_ORIGIN must be an absolute HTTPS origin.")
    if upstream_parts.path or upstream_parts.query or upstream_parts.fragment:
        raise ValueError("UPSTREAM_ORIGIN must contain only a scheme and host.")
    result_mode = os.getenv("RESULT_MODE", "rng").strip().lower()
    if result_mode not in {"rng", "admin"}:
        raise ValueError("RESULT_MODE must be rng or admin.")

    return Settings(
        environment=environment,
        public_base_url=public_base_url,
        session_secret=session_secret,
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://app:change-me@localhost:5432/newgen",
        ),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        auth_redis_url=os.getenv(
            "AUTH_REDIS_URL",
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        ),
        upstream_origin=upstream_origin,
        results_refresh_seconds=_positive_int("RESULTS_REFRESH_SECONDS", 60),
        page_cache_seconds=_positive_int("PAGE_CACHE_SECONDS", 300),
        asset_cache_seconds=_positive_int("ASSET_CACHE_SECONDS", 86400),
        stale_cache_seconds=_positive_int("STALE_CACHE_SECONDS", 3600),
        upstream_requests_per_second=_positive_float(
            "UPSTREAM_REQUESTS_PER_SECOND", 5.0
        ),
        db_pool_size=_positive_int("DB_POOL_SIZE", 5),
        db_max_overflow=_positive_int("DB_MAX_OVERFLOW", 5),
        admin_username=os.getenv("ADMIN_USERNAME", "").strip(),
        admin_password=os.getenv("ADMIN_PASSWORD", ""),
        result_mode=result_mode,
    )


settings = load_settings()
