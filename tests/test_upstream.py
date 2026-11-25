import asyncio

import httpx
import pytest
from fastapi import HTTPException

from app.upstream import (
    CachedResponse,
    RESULTS_CACHE_KEY,
    _decode_response,
    _encode_response,
    _retry_after_seconds,
    refresh_market_data,
    rewrite_site_contacts,
    rewrite_upstream_urls,
)


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expiries = {}
        self.counters = {}

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.values:
            return False
        self.values[key] = value.encode() if isinstance(value, str) else value
        if ex:
            self.expiries[key] = ex
        return True

    async def exists(self, key):
        return int(key in self.values)

    async def delete(self, *keys):
        for key in keys:
            self.values.pop(key, None)

    async def incr(self, key):
        self.counters[key] = self.counters.get(key, 0) + 1
        self.values[key] = str(self.counters[key]).encode()
        return self.counters[key]

    async def expire(self, key, seconds):
        self.expiries[key] = seconds
        return True

    async def eval(self, script, key_count, *args):
        if "HMGET" in script:
            return 0
        key, value = args
        if self.values.get(key) == value.encode():
            del self.values[key]
            return 1
        return 0


def test_rewrite_upstream_urls_preserves_paths_and_query_strings():
    content = (
        'href="https://matkaonline.games/jodi-chart/TIME-BAZAR?week=1" '
        'src="//www.matkaonline.games/assets/site.css" '
        'href="https://example.com/outside"'
    )

    rewritten = rewrite_upstream_urls(content)

    assert 'href="/jodi-chart/TIME-BAZAR?week=1"' in rewritten
    assert 'src="/assets/site.css"' in rewritten
    rewritten_logo = rewrite_upstream_urls(
        '<img src="https://matkaonline.games/assets/front/images/online-matka-logo.webp" alt="footerlogo">'
    )
    assert 'class="dhanraj-wordmark"' in rewritten_logo
    assert 'class="dhanraj-mark-d">D</span>' in rewritten_logo
    assert "online-matka-logo.webp" not in rewritten_logo
    assert "https://example.com/outside" in rewritten


def test_site_contact_rewrite_removes_old_phone_and_email_links():
    html = (
        '<a href="tel:+917773891171">+91 7773891171</a>'
        '<a href="/cdn-cgi/l/email-protection"><span class="__cf_email__">hidden</span></a>'
        '<a href="whatsapp://send?phone=+917773891171">WhatsApp</a>'
        '<p><a href="/">Play Matka Online</a> and win Real Money today.</p>'
        "<li><strong>Deposit Funds:</strong> Deposit money to your account.</li>"
        "<p>The minimum bet ammount to play in any online matka game is Rs. 10.</p>"
    )

    rewritten = rewrite_site_contacts(html)

    assert "7773891171" not in rewritten
    assert "email-protection" not in rewritten
    assert "mailto:" not in rewritten
    assert rewritten.count("https://wa.me/918699915927") >= 2
    assert "Deposit money to your account" not in rewritten
    assert "win Real Money" not in rewritten
    assert "Rs. 10" not in rewritten
    assert "nonredeemable virtual coins" in rewritten


def test_site_contact_rewrite_updates_previous_support_number():
    rewritten = rewrite_site_contacts(
        '<a href="tel:+918600110910">8600110910</a>'
        '<a href="https://wa.me/918600110910">WhatsApp</a>'
    )

    assert "+91 8699915927" in rewritten
    assert "https://wa.me/918699915927" in rewritten
    assert "8600110910" not in rewritten


def test_cached_response_round_trips_bytes_and_headers():
    response = CachedResponse(
        status_code=200,
        content_type="text/html; charset=utf-8",
        body=b"<h1>cached</h1>",
    )

    assert _decode_response(_encode_response(response)) == response


def test_invalid_cached_response_is_rejected():
    assert _decode_response(b"not-json") is None


def test_retry_after_accepts_seconds_and_rejects_invalid_values():
    assert _retry_after_seconds("15") == 15
    assert _retry_after_seconds("invalid") == 0


def test_market_results_are_fetched_once_and_shared_from_cache():
    async def exercise_refresh():
        calls = []

        async def handler(request):
            calls.append(request.url)
            return httpx.Response(200, json=[{"id": "59"}])

        redis = FakeRedis()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            assert await refresh_market_data(client, redis)
            assert await refresh_market_data(client, redis)

        assert len(calls) == 1
        assert b'"id":"59"' in redis.values[RESULTS_CACHE_KEY]

    asyncio.run(exercise_refresh())


def test_upstream_rate_limit_opens_backoff_instead_of_retrying():
    async def exercise_backoff():
        calls = []

        async def handler(request):
            calls.append(request.url)
            return httpx.Response(429, headers={"Retry-After": "30"})

        redis = FakeRedis()
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(HTTPException) as error:
                await refresh_market_data(client, redis, force=True)
            assert error.value.status_code == 503
            assert error.value.headers["Retry-After"] == "30"
            assert not await refresh_market_data(client, redis, force=True)

        assert len(calls) == 1
        assert "upstream:backoff" in redis.values

    asyncio.run(exercise_backoff())
