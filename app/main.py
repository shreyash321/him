import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from redis.asyncio import Redis
from sqlalchemy import text

from app.auth import router as auth_router
from app.auth import bootstrap_admin
from app.config import settings
from app.database import engine
from app.games import game_scheduler_loop, router as games_router
from app.pages import (
    ADMIN_PAGE,
    GAME_PAGE,
    LOGIN_PAGE,
    REGISTER_PAGE,
    WALLET_PAGE,
    inject_account_toolbar,
    inject_market_home,
)
from app.upstream import (
    get_market_results,
    market_refresh_loop,
    proxy_public_page,
    rewrite_site_contacts,
    rewrite_upstream_urls,
)
from app.wallet import router as wallet_router


APP_DIRECTORY = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_runtime()
    redis = Redis.from_url(settings.redis_url, socket_connect_timeout=5)
    auth_redis = Redis.from_url(settings.auth_redis_url, socket_connect_timeout=5)
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(10, connect=5),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        follow_redirects=False,
    )
    app.state.redis = redis
    app.state.auth_redis = auth_redis
    app.state.http = client
    try:
        await redis.ping()
        await auth_redis.ping()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        await bootstrap_admin()
        refresh_task = asyncio.create_task(
            market_refresh_loop(client, redis, auth_redis)
        )
        game_task = asyncio.create_task(game_scheduler_loop())
        try:
            yield
        finally:
            for task in (refresh_task, game_task):
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    finally:
        await client.aclose()
        await redis.aclose()
        await auth_redis.aclose()
        await engine.dispose()


app = FastAPI(
    title="DhanRAJ",
    lifespan=lifespan,
    docs_url=None if settings.production else "/docs",
    redoc_url=None if settings.production else "/redoc",
)
app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(games_router)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    if request.url.path.startswith("/auth/") or request.url.path in {
        "/login",
        "/register",
        "/registration",
        "/wallet",
        "/admin",
        "/virtual-game",
        "/virtual-game/rates",
    }:
        response.headers["Cache-Control"] = "no-store"
    if settings.production:
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


@app.get("/healthz")
async def health():
    return {"status": "ok"}


@app.get("/readyz")
async def readiness(request: Request):
    try:
        await request.app.state.redis.ping()
        await request.app.state.auth_redis.ping()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A required service is not ready.",
        ) from error
    return {"status": "ready"}


@app.get("/front/fetch_updated_results")
async def market_results(request: Request):
    return await get_market_results(request)


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(LOGIN_PAGE)


@app.get("/register", response_class=HTMLResponse)
@app.get("/registration", response_class=HTMLResponse)
async def registration_page():
    return HTMLResponse(REGISTER_PAGE)


@app.get("/wallet", response_class=HTMLResponse)
async def wallet_page():
    return HTMLResponse(WALLET_PAGE)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return HTMLResponse(ADMIN_PAGE)


@app.get("/virtual-game", response_class=HTMLResponse)
@app.get("/virtual-game/rates", response_class=HTMLResponse)
async def game_page():
    return HTMLResponse(GAME_PAGE)


@app.get("/deposit")
@app.get("/withdraw")
async def virtual_wallet_actions():
    return RedirectResponse("/wallet", status_code=status.HTTP_303_SEE_OTHER)


@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/{path:path}", methods=["GET", "HEAD"])
async def public_site_proxy(request: Request, path: str = ""):
    try:
        response = await proxy_public_page(request, path)
        if (
            not path
            and
            request.method == "GET"
            and response.status_code == status.HTTP_200_OK
            and response.headers.get("content-type", "").lower().startswith("text/html")
        ):
            headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() not in {"content-length", "content-type", "cache-control"}
            }
            headers["Cache-Control"] = "private, no-store"
            content = inject_market_home(
                response.body.decode("utf-8", errors="replace")
            )
            return HTMLResponse(
                inject_account_toolbar(content),
                status_code=response.status_code,
                headers=headers,
            )
        return response
    except HTTPException as error:
        if path or error.status_code != status.HTTP_503_SERVICE_UNAVAILABLE:
            raise

        fallback_path = APP_DIRECTORY / "main.html"
        if not fallback_path.is_file():
            raise
        content = fallback_path.read_text(encoding="utf-8")
        return HTMLResponse(
            inject_account_toolbar(
                inject_market_home(
                    rewrite_site_contacts(rewrite_upstream_urls(content))
                )
            ),
            headers={"X-Proxy-Cache": "LOCAL-FALLBACK", "Cache-Control": "no-store"},
        )
