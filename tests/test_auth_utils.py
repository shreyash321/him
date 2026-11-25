import pytest

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.auth import _require_same_origin
from app.auth import _session_key, normalize_phone, password_hash


def test_phone_normalization_accepts_indian_local_and_international_numbers():
    assert normalize_phone("8600110910") == "+918600110910"
    assert normalize_phone("+91 86001-10910") == "+918600110910"


def test_same_origin_validation_accepts_https_behind_cloudflare_proxy():
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/login",
            "query_string": b"",
            "headers": [
                (b"host", b"sample.trycloudflare.com"),
                (b"origin", b"https://sample.trycloudflare.com"),
                (b"x-forwarded-proto", b"https"),
            ],
            "server": ("127.0.0.1", 8000),
            "client": ("127.0.0.1", 12345),
        }
    )

    _require_same_origin(request)


def test_same_origin_validation_rejects_mismatched_host():
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/login",
            "query_string": b"",
            "headers": [
                (b"host", b"sample.trycloudflare.com"),
                (b"origin", b"https://attacker.example"),
                (b"x-forwarded-proto", b"https"),
            ],
            "server": ("127.0.0.1", 8000),
            "client": ("127.0.0.1", 12345),
        }
    )

    with pytest.raises(HTTPException) as error:
        _require_same_origin(request)
    assert error.value.status_code == 403


def test_session_keys_are_not_the_raw_session_token():
    token = "sample-session-token"

    key = _session_key(token)

    assert key.startswith("auth:session:")
    assert token not in key
    assert _session_key(token) == key
    assert _session_key("different-token") != key


def test_password_hash_verifies_only_the_original_password():
    hashed = password_hash.hash("a-long-password-that-is-not-stored")

    assert password_hash.verify("a-long-password-that-is-not-stored", hashed)
    assert not password_hash.verify("incorrect-password", hashed)
