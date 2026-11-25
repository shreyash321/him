import asyncio
from dataclasses import replace

import httpx
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.auth as auth
import app.wallet as wallet
from app.database import Base
from app.models import CoinTransaction, User
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


def test_phone_registration_virtual_bets_admin_credits_and_logout(monkeypatch, tmp_path):
    async def exercise_flow():
        database_path = tmp_path / "accounts.db"
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
                admin_username="admin111",
                admin_password="bootstrap-password",
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
                        "username": "player_1",
                        "phone": "8600110099",
                        "password": "a-strong-password",
                    },
                )
                assert registration.status_code == 201
                assert registration.json()["registered"] is True
                assert "created successfully" in registration.json()["message"]
                duplicate_registration = await client.post(
                    "/auth/register",
                    headers=origin,
                    json={
                        "username": "player_1",
                        "phone": "8600110099",
                        "password": "a-strong-password",
                    },
                )
                assert duplicate_registration.status_code == 409
                assert "may already be in use" in duplicate_registration.json()["detail"]
                async with session_factory() as session:
                    player = await session.scalar(
                        select(User).where(User.username == "player_1")
                    )
                    assert player.phone == "+918600110099"
                    assert player.email is None
                    assert player.coin_balance == 0
                    assert not player.password_hash.startswith("a-strong-password")
                    signup_transactions = await session.scalars(
                        select(CoinTransaction).where(
                            CoinTransaction.user_id == player.id
                        )
                    )
                    assert list(signup_transactions) == []

                login = await client.post(
                    "/auth/login",
                    headers=origin,
                    json={"identifier": "8600110099", "password": "a-strong-password"},
                )
                assert login.status_code == 200
                assert login.json()["role"] == "user"
                assert "site_session" in client.cookies
                assert "site_csrf" in client.cookies

                csrf_headers = {
                    **origin,
                    "X-CSRF-Token": client.cookies.get("site_csrf"),
                }
                unfunded_bet = await client.post(
                    "/wallet/bets",
                    headers=csrf_headers,
                    json={"market": "Market A", "selection": "42", "amount": 1},
                )
                assert unfunded_bet.status_code == 409
                credited = await client.post(
                    "/admin/credits",
                    headers=csrf_headers,
                    json={
                        "username": "player_1",
                        "phone": "8600110099",
                        "amount": 100,
                    },
                )
                assert credited.status_code == 403
                debited = await client.post(
                    "/admin/debits",
                    headers=csrf_headers,
                    json={
                        "username": "player_1",
                        "phone": "8600110099",
                        "amount": 1,
                    },
                )
                assert debited.status_code == 403

                await auth.bootstrap_admin()
                async with session_factory() as session:
                    admin = await session.scalar(
                        select(User).where(User.username == "admin111")
                    )
                    assert admin.role == "admin"
                    assert admin.must_change_password
                    assert not admin.password_hash.startswith("bootstrap-password")

                admin_login = await client.post(
                    "/auth/login",
                    headers=origin,
                    json={"identifier": "admin111", "password": "bootstrap-password"},
                )
                assert admin_login.status_code == 200
                assert admin_login.json()["must_change_password"]

                changed = await client.post(
                    "/auth/change-password",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                    json={
                        "current_password": "bootstrap-password",
                        "new_password": "a-new-strong-admin-password",
                    },
                )
                assert changed.status_code == 200
                credit = await client.post(
                    "/admin/credits",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                    json={
                        "username": "player_1",
                        "phone": "+91 8600110099",
                        "amount": 100,
                    },
                )
                assert credit.status_code == 201
                assert credit.json()["coin_balance"] == 100
                admin_csrf_headers = {
                    **origin,
                    "X-CSRF-Token": client.cookies.get("site_csrf"),
                }
                debit = await client.post(
                    "/admin/debits",
                    headers=admin_csrf_headers,
                    json={
                        "username": "player_1",
                        "phone": "8600110099",
                        "amount": 30,
                    },
                )
                assert debit.status_code == 201
                assert debit.json()["amount_removed"] == 30
                assert debit.json()["coin_balance"] == 70
                insufficient_debit = await client.post(
                    "/admin/debits",
                    headers=admin_csrf_headers,
                    json={
                        "username": "player_1",
                        "phone": "8600110099",
                        "amount": 1071,
                    },
                )
                assert insufficient_debit.status_code == 409
                assert "not have enough" in insufficient_debit.json()["detail"]
                mismatched_debit = await client.post(
                    "/admin/debits",
                    headers=admin_csrf_headers,
                    json={
                        "username": "player_1",
                        "phone": "8600110000",
                        "amount": 1,
                    },
                )
                assert mismatched_debit.status_code == 404

                await client.post(
                    "/auth/logout",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                )
                player_login = await client.post(
                    "/auth/login",
                    headers=origin,
                    json={"identifier": "player_1", "password": "a-strong-password"},
                )
                assert player_login.status_code == 200
                bet = await client.post(
                    "/wallet/bets",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                    json={"market": "Market A", "selection": "42", "amount": 25},
                )
                assert bet.status_code == 201
                assert bet.json()["coin_balance"] == 45
                insufficient = await client.post(
                    "/wallet/bets",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                    json={"market": "Market A", "selection": "43", "amount": 1046},
                )
                assert insufficient.status_code == 409

                history = await client.get("/wallet/history")
                assert history.status_code == 200
                assert history.json()["coin_balance"] == 45
                assert history.json()["coins_are_redeemable"] is False
                assert len(history.json()["transactions"]) == 3
                assert {
                    (transaction["kind"], transaction["amount_delta"])
                    for transaction in history.json()["transactions"]
                } == {
                    ("bet_debit", -25),
                    ("admin_debit", -30),
                    ("admin_credit", 100),
                }
                async with session_factory() as session:
                    rows = list(await session.scalars(select(CoinTransaction)))
                    assert len(rows) == 3
                    assert sum(row.amount_delta for row in rows) == 45

                async with session_factory() as session:
                    player = await session.scalar(
                        select(User).where(User.username == "player_1")
                    )
                    session.add_all(
                        [
                            CoinTransaction(
                                user_id=player.id,
                                kind="admin_credit",
                                amount_delta=1,
                                balance_after=1045,
                                description="History retention check",
                            )
                            for _ in range(101)
                        ]
                    )
                    await session.commit()
                complete_history = await client.get("/wallet/history")
                assert len(complete_history.json()["transactions"]) == 104

                logout = await client.post(
                    "/auth/logout",
                    headers={
                        **origin,
                        "X-CSRF-Token": client.cookies.get("site_csrf"),
                    },
                )
                assert logout.status_code == 200
                assert (await client.get("/auth/me")).status_code == 401
        finally:
            await engine.dispose()

    asyncio.run(exercise_flow())
