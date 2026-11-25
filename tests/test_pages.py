import asyncio

import httpx
from fastapi import HTTPException, Response

import app.main as main
from app.main import app
from app.pages import inject_account_toolbar, inject_market_home


def test_auth_pages_are_local_and_not_cacheable():
    async def request_pages():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            login = await client.get("/login")
            register = await client.get("/registration")
            wallet = await client.get("/wallet")
            admin = await client.get("/admin")
            game = await client.get("/virtual-game")
            rates = await client.get("/virtual-game/rates")
            deposit = await client.get("/deposit", follow_redirects=False)
            withdrawal = await client.get("/withdraw", follow_redirects=False)
        return login, register, wallet, admin, game, rates, deposit, withdrawal

    login, register, wallet, admin, game, rates, deposit, withdrawal = asyncio.run(request_pages())

    assert login.status_code == 200
    assert "Log in | DhanRAJ" in login.text
    assert 'class="dhanraj-wordmark"' in login.text
    assert 'class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ' in login.text
    assert "#DC2626" in login.text
    assert "Log in" in login.text
    assert "phone number" in login.text
    assert "class=\"auth-card\"" in login.text
    assert "--wine:#60132f" in login.text
    assert 'href="/virtual-game">KINGSTARLINE</a>' in login.text
    assert "/single" not in login.text
    assert "/jodi" not in login.text
    assert "SINGLE PATTI" not in login.text
    assert "DOUBLE PATTI" not in login.text
    assert 'location.assign(result.role==="admin"||result.must_change_password?"/admin":"/wallet")' in login.text
    assert register.status_code == 200
    assert "Create account | DhanRAJ" in register.text
    assert 'id="registration-dialog"' in register.text
    assert "Registration successful" in register.text
    assert "Registration unsuccessful" in register.text
    assert "dialog.showModal()" in register.text
    assert 'response.status!==201||result.registered!==true' in register.text
    assert 'class="footer-brand" href="/" aria-label="DhanRAJ home"' in register.text
    assert "Create account" in register.text
    assert "Phone ownership is not verified" in register.text
    assert "virtual coins have no cash value" in register.text
    assert wallet.status_code == 200
    assert "My account | DhanRAJ" in wallet.text
    assert 'data-dhanraj-support' in wallet.text
    assert "918699915927" in wallet.text
    assert "918437691436" not in wallet.text
    assert "Message support on WhatsApp · 8699915927" in wallet.text
    assert 'whatsappUrl("918699915927",text)' in wallet.text
    assert "Request credit (add virtual coins)" in wallet.text
    assert "Request debit (remove virtual coins)" in wallet.text
    assert "VIRTUAL COIN BALANCE" in wallet.text
    assert 'data-tab="bids"' in wallet.text
    assert 'data-tab="passbook"' in wallet.text
    assert 'data-tab="funds"' in wallet.text
    assert "My Activity" in wallet.text
    assert "Passbook" in wallet.text
    assert "Credited" in wallet.text
    assert "Debited" in wallet.text
    assert "Record entry" not in wallet.text
    assert 'id="activity"' in wallet.text
    assert 'id="history"' in wallet.text
    assert "Virtual coin center" in wallet.text
    assert "data-open-tab=\"fund-request\"" in wallet.text
    assert "WhatsApp support" in wallet.text
    assert "No cash deposits, withdrawals, or payouts" in wallet.text
    assert "showHashTab" in wallet.text
    assert admin.status_code == 200
    assert "Admin | DhanRAJ" in admin.text
    assert "Grant virtual coins" in admin.text
    assert "Never ask for a user's password" in admin.text
    assert 'id="debit"' in admin.text
    assert 'wireCoinAdjustment("debit","/admin/debits"' in admin.text
    assert "Debit virtual coins" in admin.text
    assert 'id="credit-feedback"' in admin.text
    assert 'result==="error"?"alert":"status"' in admin.text
    assert "Transaction failed: ${error.message}" in admin.text
    assert "Success: ${verb} ${amount} virtual coins" in admin.text
    assert game.status_code == 200
    assert "KingStarline" in game.text
    assert "Single Digit" in game.text
    assert "Jodi Digit" in game.text
    assert "Single Panna" in game.text
    assert "Double Panna" in game.text
    assert "Triple Panna" in game.text
    assert "Daily Bonus" not in game.text
    assert "Free Refill" not in game.text
    assert "Half Sangam" not in game.text
    assert "Full Sangam" not in game.text
    assert rates.status_code == 200
    assert "Win Rates" in rates.text
    assert deposit.status_code == 303
    assert deposit.headers["location"] == "/wallet"
    assert withdrawal.status_code == 303
    assert withdrawal.headers["location"] == "/wallet"
    for response in (login, register, wallet, admin):
        assert response.headers["cache-control"] == "no-store"


def test_account_toolbar_injection_is_idempotent():
    html = "<html><body><header class='top_header'></header></body></html>"

    injected = inject_account_toolbar(html)

    assert 'id="newgen-account-toolbar"' in injected
    assert inject_account_toolbar(injected) == injected


def test_market_home_injection_is_idempotent_and_requires_results_section():
    html = (
        "<html><body><main><section id=\"bet-results-section\">"
        "<div id=\"bet-results-container\"></div></section></main></body></html>"
    )

    injected = inject_market_home(html)

    assert 'id="newgen-market-home"' in injected
    assert "logo.innerHTML=" in injected
    assert "dhanraj-mark-d" in injected
    assert "dhanraj-mark-raj" in injected
    assert "918699915927" in injected
    assert 'id="market-data-status"' in injected
    assert "/front/fetch_updated_results" in injected
    assert 'href="/virtual-game"' in injected
    assert "Tap to Play" in injected
    assert "width:min(100%,360px);margin:0 auto" in injected
    assert '<p class="muted">Virtual points only. No real money. For entertainment.</p>' not in injected
    assert "kingstarline-glow" in injected
    assert "kingstarline-modal" not in injected
    assert "game-option" not in injected
    assert "Single Digit" not in injected
    assert "Daily Bonus" not in injected
    assert "Free Refill" not in injected
    assert "setInterval(refresh,60000)" in injected
    assert inject_market_home(injected) == injected
    assert inject_market_home("<html><body>No market data</body></html>") == (
        "<html><body>No market data</body></html>"
    )


def test_public_html_injects_account_toolbar_without_client_caching(monkeypatch):
    async def proxy_page(request, path):
        return Response(
            content=(
                "<html><body><header class='top_header'></header><main>"
                "<section id=\"bet-results-section\"><div "
                "id=\"bet-results-container\"></div></section></main></body></html>"
            ),
            media_type="text/html",
        )

    async def request_home():
        monkeypatch.setattr(main, "proxy_public_page", proxy_page)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/")

    response = asyncio.run(request_home())

    assert response.status_code == 200
    assert 'id="newgen-account-toolbar"' in response.text
    assert 'id="newgen-market-home"' in response.text
    assert response.headers["cache-control"] == "private, no-store"


def test_local_fallback_uses_new_brand_and_support_contact(monkeypatch):
    async def unavailable(request, path):
        raise HTTPException(status_code=503, detail="upstream unavailable")

    async def request_home():
        monkeypatch.setattr(main, "proxy_public_page", unavailable)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get("/")

    response = asyncio.run(request_home())

    assert response.status_code == 200
    assert 'class="dhanraj-wordmark"' in response.text
    assert "/static/dhanraj-logo.png" not in response.text
    assert "https://wa.me/918699915927" in response.text
    assert "8600110910" not in response.text
    assert "7773891171" not in response.text
