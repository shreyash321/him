import asyncio
from dataclasses import replace

import httpx
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.auth as auth
import app.wallet as wallet
from app.database import Base
from app.models import CreditRequest, User, WithdrawalRequest
from app.wallet import router as wallet_router


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.counters = {}

    def pipeline(self, transaction=True):
        return FakePipeline(self)

    async def incr(self, key):
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    async def expire(self, key, seconds):
        return True

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.values:
            return False
        self.values[key] = value.encode() if isinstance(value, str) else value
        return True

    async def delete(self, key):
        self.values.pop(key, None)


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    def incr(self, key):
        self.commands.append(("incr", key))

    def expire(self, key, seconds):
        self.commands.append(("expire", key, seconds))

    async def execute(self):
        results = []
        for command in self.commands:
            if command[0] == "incr":
                results.append(await self.redis.incr(command[1]))
            else:
                results.append(await self.redis.expire(command[1], command[2]))
        return results


def test_credit_and_withdrawal_request_flow_and_admin_approval(monkeypatch, tmp_path):
    async def exercise_flow():
        database_path = tmp_path / "request-management.db"
        engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        monkeypatch.setattr(auth, "SessionFactory", session_factory)
        monkeypatch.setattr(wallet, "SessionFactory", session_factory)
        monkeypatch.setattr(
            auth,
            "settings",
            replace(
                auth.settings,
                admin_username="admin_req",
                admin_password="bootstrap-pass-strong",
            ),
        )

        application = FastAPI()
        application.include_router(auth.router)
        application.include_router(wallet_router)
        application.state.auth_redis = FakeRedis()
        transport = httpx.ASGITransport(app=application)
        origin = {"Origin": "http://127.0.0.1:8000"}

        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://127.0.0.1:8000",
            ) as client:
                registration = await client.post(
                    "/auth/register",
                    headers=origin,
                    json={
                        "username": "player_req",
                        "phone": "9000012345",
                        "password": "a-strong-password",
                    },
                )
                assert registration.status_code == 201

                login = await client.post(
                    "/auth/login",
                    headers=origin,
                    json={"identifier": "player_req", "password": "a-strong-password"},
                )
                assert login.status_code == 200
                csrf_headers = {
                    **origin,
                    "X-CSRF-Token": client.cookies.get("site_csrf"),
                }

                small_credit = await client.post(
                    "/api/requests/credit",
                    headers=csrf_headers,
                    json={"amount": 400},
                )
                assert small_credit.status_code == 422

                credit = await client.post(
                    "/api/requests/credit",
                    headers=csrf_headers,
                    json={"amount": 500},
                )
                assert credit.status_code == 201
                assert credit.json()["status"] == "PENDING"

                async with session_factory() as session:
                    user = await session.scalar(select(User).where(User.username == "player_req"))
                    user.coin_balance = 2000
                    await session.commit()

                small_withdraw = await client.post(
                    "/api/requests/withdraw",
                    headers=csrf_headers,
                    json={
                        "amount": 500,
                        "account_holder_name": "Player Req",
                        "bank_account_number": "1234567890",
                        "ifsc_code": "ABCD0123456",
                    },
                )
                assert small_withdraw.status_code == 422

                insufficient = await client.post(
                    "/api/requests/withdraw",
                    headers=csrf_headers,
                    json={
                        "amount": 2500,
                        "account_holder_name": "Player Req",
                        "bank_account_number": "1234567890",
                        "ifsc_code": "ABCD0123456",
                    },
                )
                assert insufficient.status_code == 409

                first_withdraw = await client.post(
                    "/api/requests/withdraw",
                    headers=csrf_headers,
                    json={
                        "amount": 1000,
                        "account_holder_name": "Player Req",
                        "bank_account_number": "1234567890",
                        "ifsc_code": "ABCD0123456",
                    },
                )
                assert first_withdraw.status_code == 201
                assert first_withdraw.json()["status"] == "PENDING"

                second_withdraw = await client.post(
                    "/api/requests/withdraw",
                    headers=csrf_headers,
                    json={"amount": 500},
                )
                assert second_withdraw.status_code == 201
                assert second_withdraw.json()["bank_account_number"] == "1234567890"

                async with session_factory() as session:
                    user = await session.scalar(select(User).where(User.username == "player_req"))
                    assert user.account_holder_name == "Player Req"
                    assert user.bank_account_number == "1234567890"
                    assert user.ifsc_code == "ABCD0123456"
                    withdrawal_count = await session.scalar(
                        select(WithdrawalRequest).where(WithdrawalRequest.user_id == user.id)
                    )
                    assert withdrawal_count is not None

                await auth.bootstrap_admin()
                admin_login = await client.post(
                    "/auth/login",
                    headers=origin,
                    json={"identifier": "admin_req", "password": "bootstrap-pass-strong"},
                )
                assert admin_login.status_code == 200
                assert admin_login.json()["must_change_password"] is True

                changed = await client.post(
                    "/auth/change-password",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                    json={
                        "current_password": "bootstrap-pass-strong",
                        "new_password": "a-new-strong-admin-password",
                    },
                )
                assert changed.status_code == 200
                admin_csrf_headers = {
                    **origin,
                    "X-CSRF-Token": client.cookies.get("site_csrf"),
                }

                list_requests = await client.get(
                    "/api/admin/requests?type=all&search=player_req",
                    headers={"Origin": "http://127.0.0.1:8000"},
                )
                assert list_requests.status_code == 200
                items = list_requests.json()["items"]
                assert any(item["type"] == "credit" and item["status"] == "PENDING" for item in items)
                credit_id = next(item["id"] for item in items if item["type"] == "credit")
                approve_credit = await client.post(
                    f"/api/admin/requests/{credit_id}/approve",
                    headers=admin_csrf_headers,
                    json={},
                )
                assert approve_credit.status_code == 200
                assert approve_credit.json()["status"] == "APPROVED"

                duplicate = await client.post(
                    f"/api/admin/requests/{credit_id}/approve",
                    headers=admin_csrf_headers,
                    json={},
                )
                assert duplicate.status_code == 409

                async with session_factory() as session:
                    user = await session.scalar(select(User).where(User.username == "player_req"))
                    assert user.coin_balance == 2500

                pending_withdrawals = [
                    item for item in items if item["type"] == "withdrawal" and item["status"] == "PENDING"
                ]
                assert pending_withdrawals
                withdraw_id = pending_withdrawals[0]["id"]
                approve_withdrawal = await client.post(
                    f"/api/admin/requests/{withdraw_id}/approve",
                    headers=admin_csrf_headers,
                    json={},
                )
                assert approve_withdrawal.status_code == 200
                assert approve_withdrawal.json()["wallet_balance"] == 1500

                async with session_factory() as session:
                    user = await session.scalar(select(User).where(User.username == "player_req"))
                    assert user.coin_balance == 1500
        finally:
            await engine.dispose()

    asyncio.run(exercise_flow())
