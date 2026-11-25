import asyncio
import base64
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException, Request, Response, status
from redis.asyncio import Redis

from app.config import settings


logger = logging.getLogger(__name__)
RESULTS_PATH = "/front/fetch_updated_results"
RESULTS_CACHE_KEY = "cache:market-results:v1"
RESULTS_STALE_CACHE_KEY = "cache:market-results:v1:stale"
MAX_UPSTREAM_RESPONSE_BYTES = 8 * 1024 * 1024
UPSTREAM_HOST = urlsplit(settings.upstream_origin).hostname
UPSTREAM_URL_PATTERN = re.compile(
    rf"(?i)(?:https?:)?//(?:www\.)?{re.escape(UPSTREAM_HOST or '')}(?::\d+)?"
)
STATIC_SUFFIXES = (
    ".avif",
    ".css",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".map",
    ".png",
    ".svg",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
)
LEGACY_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?91[\s().-]*)?777[\s().-]*389[\s().-]*1171(?!\d)"
)
OLD_SUPPORT_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?91[\s().-]*)?860[\s().-]*011[\s().-]*0910(?!\d)"
)
PROTECTED_EMAIL_LINK_PATTERN = re.compile(
    r"<a\b(?=[^>]*email-protection)[^>]*>.*?</a>", re.IGNORECASE | re.DOTALL
)
WHATSAPP_LINK_PATTERN = re.compile(
    r"whatsapp://send\?[^\"'\s<>]*", re.IGNORECASE
)
WA_ME_LINK_PATTERN = re.compile(
    r"https?://(?:www\.)?wa\.me/\d+(?:\?[^\s\"'<>]*)?", re.IGNORECASE
)
RELEASE_LOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
  return redis.call("del", KEYS[1])
end
return 0
"""
UPSTREAM_TOKEN_SCRIPT = """
local now = redis.call("TIME")
local now_ms = tonumber(now[1]) * 1000 + math.floor(tonumber(now[2]) / 1000)
local values = redis.call("HMGET", KEYS[1], "tokens", "updated")
local rate = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local tokens = tonumber(values[1]) or capacity
local updated = tonumber(values[2]) or now_ms
tokens = math.min(capacity, tokens + math.max(0, now_ms - updated) * rate / 1000)
if tokens < 1 then
  redis.call("HSET", KEYS[1], "tokens", tokens, "updated", now_ms)
  redis.call("PEXPIRE", KEYS[1], math.ceil(capacity / rate * 2000))
  return math.ceil((1 - tokens) / rate * 1000)
end
tokens = tokens - 1
redis.call("HSET", KEYS[1], "tokens", tokens, "updated", now_ms)
redis.call("PEXPIRE", KEYS[1], math.ceil(capacity / rate * 2000))
return 0
"""


@dataclass(frozen=True)
class CachedResponse:
    status_code: int
    content_type: str
    body: bytes
    location: str | None = None
    cache_status: str = "MISS"


def rewrite_upstream_urls(content: str) -> str:
    content = UPSTREAM_URL_PATTERN.sub("", content)
    return re.sub(
        r"""<img\b(?=[^>]*\bsrc\s*=\s*['"][^'"]*/?online-matka-logo\.webp['"])[^>]*>""",
        '<span class="dhanraj-wordmark" aria-label="DhanRAJ"><span class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ</span></span>',
        content,
        flags=re.IGNORECASE,
    )


def rewrite_site_contacts(content: str) -> str:
    content = WA_ME_LINK_PATTERN.sub("https://wa.me/918699915927", content)
    content = WHATSAPP_LINK_PATTERN.sub("https://wa.me/918699915927", content)
    content = PROTECTED_EMAIL_LINK_PATTERN.sub(
        '<a href="https://wa.me/918699915927">WhatsApp support</a>', content
    )
    content = re.sub(
        r"(?i)mailto:[^\"'\s<>]+",
        "https://wa.me/918699915927",
        content,
    )
    content = LEGACY_PHONE_PATTERN.sub("+91 8699915927", content)
    content = OLD_SUPPORT_PHONE_PATTERN.sub("+91 8699915927", content)
    replacements = (
        (
            r"<p><a\b[^>]*>Play Matka Online</a> and win Real Money.*?</p>",
            "<p>Explore market results and record virtual coin entries. Virtual coins have no cash value; this website does not accept deposits or pay winnings.</p>",
        ),
        (
            r"<li><strong>Deposit Funds:</strong>.*?</li>",
            "<li><strong>Virtual credits:</strong> Request nonredeemable virtual coins from your wallet support page.</li>",
        ),
        (
            r"<li><strong>Accumilate Winnings:</strong>.*?</li>",
            "<li><strong>Virtual results:</strong> This app records virtual coin entries only and does not provide winnings or payouts.</li>",
        ),
        (
            r"<li><b>Set a money limit:</b>.*?</li>",
            "<li><b>Set a virtual coin limit:</b> Only use virtual coins you are willing to spend.</li>",
        ),
        (
            r"<p>Playing safe online matka is a challenge.*?</p>",
            "<p>Use the wallet page for virtual coin entries. This website does not process payments or cash payouts.</p>",
        ),
        (
            r"<p>To deposit money for playing matka online.*?</p>",
            "<p>This app does not accept deposits or process withdrawals. Virtual coins have no cash value; use the wallet page to request a manual virtual credit.</p>",
        ),
        (
            r"<p>The user need not explicitly claim winnings.*?</p>",
            "<p>This app does not award winnings or support cash withdrawals. Virtual coin entries are recorded in your wallet history only.</p>",
        ),
        (
            r"<p>The minimum bet ammount to play in any online matka game.*?</p>",
            "<p>Virtual bet amounts are entered in coins on your wallet page. Each entry must be between 1 and 1,000,000 coins and cannot exceed your available balance.</p>",
        ),
        (
            r"<p>Playing Satta Matka online can be a great way to build cash.*?</p>",
            "<p>This website's wallet feature uses nonredeemable virtual coins only. It does not accept money or pay cash winnings.</p>",
        ),
        (
            r"<p>Who wouldn't want to earn money from the comfort of their own home\?.*?</p>",
            "",
        ),
    )
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(
        r"How Do I Deposit Money To Play Matka",
        "How Do I Request Virtual Coin Credits",
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(
        r"How Can i claim my winnings",
        "Can I withdraw or redeem virtual coins",
        content,
        flags=re.IGNORECASE,
    )
    return content


def _cache_key(path_and_query: str) -> str:
    digest = hashlib.sha256(path_and_query.encode("utf-8")).hexdigest()
    return f"cache:page:v6:{digest}"


def _encode_response(response: CachedResponse) -> bytes:
    return json.dumps(
        {
            "status": response.status_code,
            "content_type": response.content_type,
            "body": base64.b64encode(response.body).decode("ascii"),
            "location": response.location,
        },
        separators=(",", ":"),
    ).encode("utf-8")


def _decode_response(value: bytes | str | None) -> CachedResponse | None:
    if value is None:
        return None
    try:
        record = json.loads(value)
        body = base64.b64decode(record["body"], validate=True)
        status_code = int(record["status"])
        if not (200 <= status_code < 300 or 300 <= status_code < 400):
            return None
        return CachedResponse(
            status_code,
            str(record["content_type"]),
            body,
            record.get("location"),
        )
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _retry_after_seconds(value: str | None) -> int:
    if value:
        try:
            return max(1, int(value))
        except ValueError:
            try:
                date = parsedate_to_datetime(value)
                return max(1, int((date - datetime.now(timezone.utc)).total_seconds()))
            except (TypeError, ValueError, OverflowError):
                pass
    return 0


async def _enter_backoff(redis: Redis, retry_after: int = 0) -> int:
    failures_key = "upstream:failures"
    failures = await redis.incr(failures_key)
    if failures == 1:
        await redis.expire(failures_key, 3600)
    delay = min(30 * (2 ** min(failures - 1, 6)), 1800)
    delay = max(delay, retry_after)
    await redis.set("upstream:backoff", "1", ex=delay)
    return delay


async def _acquire_upstream_slot(redis: Redis) -> int:
    rate = settings.upstream_requests_per_second
    return int(
        await redis.eval(
            UPSTREAM_TOKEN_SCRIPT,
            1,
            "upstream:request-rate",
            rate,
            max(1, rate),
        )
    )


async def _wait_for_upstream_slot(redis: Redis) -> None:
    while True:
        wait_ms = await _acquire_upstream_slot(redis)
        if wait_ms <= 0:
            return
        await asyncio.sleep(wait_ms / 1000)


async def _fetch_market_records(
    client: httpx.AsyncClient,
    coordination_redis: Redis,
) -> list[dict]:
    try:
        await _wait_for_upstream_slot(coordination_redis)
        response = await client.get(
            f"{settings.upstream_origin}{RESULTS_PATH}",
            headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, json.JSONDecodeError, ValueError) as error:
        retry_after = 0
        if isinstance(error, httpx.HTTPStatusError):
            upstream_response = error.response
            retry_after = _retry_after_seconds(upstream_response.headers.get("Retry-After"))
            if upstream_response.status_code == 403:
                retry_after = max(retry_after, 300)
        delay = await _enter_backoff(coordination_redis, retry_after)
        logger.warning("Market data source failed; backing off for %s seconds.", delay)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data source is temporarily unavailable.",
            headers={"Retry-After": str(delay)},
        ) from error

    if not isinstance(payload, list) or any(
        not isinstance(record, dict) or "id" not in record for record in payload
    ):
        delay = await _enter_backoff(coordination_redis)
        logger.warning("Market data source returned an invalid response.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data source returned an invalid response.",
            headers={"Retry-After": str(delay)},
        )
    return payload


async def _fetch_page_response(
    client: httpx.AsyncClient,
    url: str,
) -> tuple[int, str, str | None, str | None, bytes]:
    async with client.stream(
        "GET",
        url,
        headers={
            "Accept": "text/html, application/xhtml+xml, application/json, */*",
            "User-Agent": "DhanRAJ-Site-Cache/1.0",
        },
    ) as response:
        content_type = response.headers.get("content-type", "application/octet-stream")
        status_code = response.status_code
        location = response.headers.get("location")
        retry_after = response.headers.get("Retry-After")
        if 300 <= status_code < 400:
            return status_code, content_type, location, retry_after, b""

        content_length = response.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_UPSTREAM_RESPONSE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="The page source returned a response that is too large.",
                    )
            except ValueError:
                pass

        body = bytearray()
        async for chunk in response.aiter_bytes():
            body.extend(chunk)
            if len(body) > MAX_UPSTREAM_RESPONSE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="The page source returned a response that is too large.",
                )
        return status_code, content_type, location, retry_after, bytes(body)


async def refresh_market_data(
    client: httpx.AsyncClient,
    redis: Redis,
    *,
    force: bool = False,
    coordination_redis: Redis | None = None,
) -> bool:
    coordination = coordination_redis or redis
    cached = await redis.get(RESULTS_CACHE_KEY)
    if cached and not force:
        return True

    if await coordination.exists("upstream:backoff"):
        return False

    lock_value = str(time.time_ns())
    lock_key = "lock:market-results-refresh"
    if not await coordination.set(lock_key, lock_value, nx=True, ex=30):
        return False

    try:
        if await coordination.exists("upstream:backoff"):
            return False
        records = await _fetch_market_records(client, coordination)
        payload = json.dumps(records, separators=(",", ":")).encode("utf-8")
        await redis.set(RESULTS_CACHE_KEY, payload, ex=settings.results_refresh_seconds)
        await redis.set(RESULTS_STALE_CACHE_KEY, payload, ex=settings.stale_cache_seconds)
        return True
    finally:
        await coordination.eval(RELEASE_LOCK_SCRIPT, 1, lock_key, lock_value)


async def market_refresh_loop(
    client: httpx.AsyncClient,
    redis: Redis,
    coordination_redis: Redis | None = None,
) -> None:
    while True:
        try:
            await refresh_market_data(
                client, redis, coordination_redis=coordination_redis
            )
        except HTTPException:
            pass
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Unexpected error refreshing market results.")
        await asyncio.sleep(settings.results_refresh_seconds)


async def get_market_results(request: Request) -> Response:
    redis: Redis = request.app.state.redis
    value = await redis.get(RESULTS_CACHE_KEY)
    if value is None:
        try:
            await refresh_market_data(
                request.app.state.http,
                redis,
                force=True,
                coordination_redis=request.app.state.auth_redis,
            )
        except HTTPException:
            value = await redis.get(RESULTS_STALE_CACHE_KEY)
            if value is not None:
                return Response(
                    content=value,
                    media_type="application/json",
                    headers={
                        "Cache-Control": "public, max-age=15, stale-if-error=300",
                        "X-Proxy-Cache": "STALE",
                    },
                )
            raise
        value = await redis.get(RESULTS_CACHE_KEY)
    if value is None:
        value = await redis.get(RESULTS_STALE_CACHE_KEY)
        if value is not None:
            return Response(
                content=value,
                media_type="application/json",
                headers={
                    "Cache-Control": "public, max-age=15, stale-if-error=300",
                    "X-Proxy-Cache": "STALE",
                },
            )
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market results are not available yet.",
            headers={"Retry-After": str(settings.results_refresh_seconds)},
        )

    return Response(
        content=value,
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=15, stale-while-revalidate=60",
            "X-Proxy-Cache": "HIT",
        },
    )


async def _fetch_page(
    request: Request,
    path_and_query: str,
) -> CachedResponse:
    client: httpx.AsyncClient = request.app.state.http
    redis: Redis = request.app.state.redis
    coordination: Redis = request.app.state.auth_redis
    cache_key = _cache_key(path_and_query)
    stale_key = f"{cache_key}:stale"
    fresh = _decode_response(await redis.get(cache_key))
    if fresh:
        return replace(fresh, cache_status="HIT")

    stale = _decode_response(await redis.get(stale_key))
    backoff = await coordination.ttl("upstream:backoff")
    if backoff > 0:
        if stale:
            return replace(stale, cache_status="STALE")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The page source is temporarily unavailable.",
            headers={"Retry-After": str(backoff)},
        )

    lock_key = f"lock:{cache_key}"
    lock_value = str(time.time_ns())
    if not await coordination.set(lock_key, lock_value, nx=True, ex=20):
        if stale:
            return replace(stale, cache_status="STALE")
        for _ in range(10):
            await asyncio.sleep(0.1)
            fresh = _decode_response(await redis.get(cache_key))
            if fresh:
                return replace(fresh, cache_status="HIT")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The page is being refreshed. Please retry shortly.",
            headers={"Retry-After": "2"},
        )

    try:
        if await coordination.exists("upstream:backoff"):
            if stale:
                return replace(stale, cache_status="STALE")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The page source is temporarily unavailable.",
                headers={"Retry-After": "30"},
            )

        wait_ms = await _acquire_upstream_slot(coordination)
        if wait_ms > 0:
            if stale:
                return replace(stale, cache_status="STALE")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The page source is receiving traffic. Please retry shortly.",
                headers={"Retry-After": str(max(1, (wait_ms + 999) // 1000))},
            )

        try:
            (
                upstream_status,
                upstream_content_type,
                upstream_location,
                upstream_retry_after,
                upstream_body,
            ) = await _fetch_page_response(
                client,
                f"{settings.upstream_origin}{path_and_query}",
            )
        except httpx.HTTPError as error:
            delay = await _enter_backoff(coordination)
            if stale:
                logger.warning("Page source failed; serving stale cached content.")
                return replace(stale, cache_status="STALE")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The page source is temporarily unavailable.",
                headers={"Retry-After": str(delay)},
            ) from error

        if upstream_status == 429 or upstream_status == 403:
            retry_after = _retry_after_seconds(upstream_retry_after)
            if upstream_status == 403:
                retry_after = max(retry_after, 300)
            delay = await _enter_backoff(coordination, retry_after)
            if stale:
                logger.warning(
                    "Page source returned HTTP %s; serving stale cached content.",
                    upstream_status,
                )
                return replace(stale, cache_status="STALE")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The page source is temporarily unavailable.",
                headers={"Retry-After": str(delay)},
            )

        if upstream_status >= 500:
            delay = await _enter_backoff(coordination)
            if stale:
                return replace(stale, cache_status="STALE")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The page source is temporarily unavailable.",
                headers={"Retry-After": str(delay)},
            )

        if 300 <= upstream_status < 400:
            location = upstream_location
            if location:
                location_parts = urlsplit(location)
                upstream_host = urlsplit(settings.upstream_origin).netloc.lower()
                if location_parts.netloc.lower() in {
                    upstream_host,
                    f"www.{upstream_host}",
                }:
                    location = location_parts.path or "/"
                    if location_parts.query:
                        location += f"?{location_parts.query}"
                    if location_parts.fragment:
                        location += f"#{location_parts.fragment}"
            return CachedResponse(
                status_code=upstream_status,
                content_type=upstream_content_type,
                body=b"",
                location=location,
            )
        if upstream_status >= 400:
            return CachedResponse(
                status_code=upstream_status,
                content_type=upstream_content_type,
                body=upstream_body,
            )

        content_type = upstream_content_type
        body = upstream_body
        if any(
            content_type.lower().startswith(kind)
            for kind in ("text/html", "text/css", "javascript", "application/json")
        ):
            text_body = rewrite_upstream_urls(body.decode("utf-8", errors="replace"))
            if content_type.lower().startswith("text/html"):
                text_body = rewrite_site_contacts(text_body)
            body = text_body.encode("utf-8")

        cached = CachedResponse(200, content_type, body)
        ttl = (
            settings.asset_cache_seconds
            if urlsplit(path_and_query).path.lower().endswith(STATIC_SUFFIXES)
            else settings.page_cache_seconds
        )
        entry = _encode_response(cached)
        await redis.set(cache_key, entry, ex=ttl)
        await redis.set(stale_key, entry, ex=ttl + settings.stale_cache_seconds)
        return cached
    finally:
        await coordination.eval(RELEASE_LOCK_SCRIPT, 1, lock_key, lock_value)


async def proxy_public_page(request: Request, path: str) -> Response:
    if len(path) > 2048 or len(request.url.query) > 4096:
        raise HTTPException(status_code=414, detail="Requested URL is too long.")

    full_path = f"/{path}" if path else "/"
    if full_path.startswith("//") or "\\" in full_path:
        raise HTTPException(status_code=400, detail="Invalid page path.")
    if any(segment == ".." for segment in full_path.split("/")):
        raise HTTPException(status_code=400, detail="Invalid page path.")
    path_and_query = full_path
    if request.url.query:
        path_and_query += f"?{request.url.query}"

    cached = await _fetch_page(request, path_and_query)
    cache_max_age = (
        settings.asset_cache_seconds
        if urlsplit(f"/{path}" if path else "/").path.lower().endswith(STATIC_SUFFIXES)
        else 30
    )
    headers = {
        "Content-Type": cached.content_type,
        "Cache-Control": f"public, max-age={cache_max_age}, stale-while-revalidate=60",
        "X-Proxy-Cache": cached.cache_status,
    }
    if cached.location:
        headers["Location"] = cached.location
    if request.method == "HEAD":
        return Response(status_code=cached.status_code, headers=headers)
    return Response(
        content=cached.body,
        status_code=cached.status_code,
        headers=headers,
        media_type=None,
    )
