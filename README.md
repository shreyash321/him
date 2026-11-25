# DhanRAJ website

This repository contains a provider-neutral website app with phone-based
accounts and a **nonredeemable virtual-coin ledger**.

The DhanRAJ logo appears across the homepage, login, registration, wallet, and
admin screens. Those screens use a responsive
lavender-and-burgundy theme. The account wallet has Home, My Bids, Passbook,
Coins, and Support tabs. Coin requests are support messages only; the app does
not accept deposits or provide cash withdrawals or payouts.

The homepage presents the live market results in a responsive card layout and
refreshes them from the configured upstream results endpoint every minute.

## Run locally

Requirements: Docker Desktop with Docker Compose enabled.

1. Copy `.env.example` to `.env` if you want to configure values persistently.
   Keep secrets out of source control.
2. Provide `ADMIN_USERNAME` and `ADMIN_PASSWORD` to bootstrap the first admin.
   The app will not start on an empty database without both values.
   The password is stored as an Argon2id hash in PostgreSQL, and the admin must
   change it before crediting users. Do not expose the supplied local bootstrap
   password to the internet.
3. Start the services:

   ```powershell
   docker compose up --build
   ```

4. Open `http://127.0.0.1:8000/`. Login, registration, wallet, and admin pages
   are at `/login`, `/register`, `/wallet`, and `/admin`.
   Legacy `/deposit` and `/withdraw` paths redirect to the virtual wallet.

Compose runs PostgreSQL, separate cache and auth Redis services, Alembic
migrations, and the web app. The development database password is for local use
only. Do not expose PostgreSQL or Redis to the public internet.

The existing command-line market report remains available:

```powershell
py .\fetch_market_data.py --json
```

`py .\fetch_market_data.py --serve` starts the app directly, but requires
PostgreSQL and Redis and the connection settings exported as environment
variables. The direct launcher does not load `.env` automatically.

## Accounts and admin

- Users register with a username, phone number, and password. A 10-digit
  Indian number is normalized to `+91`; other numbers should be entered in
  international format.
- Phone ownership is **not verified** because no SMS provider or OTP flow was
  selected. Login and registration have Redis-backed per-IP rate limits, and
  login additionally limits attempts for each account/IP pair. These controls
  reduce abuse but do not prove phone ownership or stop distributed bots.
  Do not expose this version publicly without phone verification and suitable
  bot protection.
- Passwords use Argon2id hashes and require at least 12 characters. Sessions
  are opaque Redis records with `HttpOnly`, `SameSite=Lax` cookies. Production
  cookies require HTTPS. State-changing wallet/admin requests require
  same-origin and CSRF checks.
- Initial admin credentials come from `ADMIN_USERNAME` and `ADMIN_PASSWORD`;
  the bootstrap password is hashed in the database and must be changed after
  the first admin login. Provide these through a local ignored `.env` or your
  deployment secret manager, never in source control.
- The provided admin username and password are bootstrap credentials only,
  not production credentials. Use a unique strong admin password before any
  public deployment.

Older email-based accounts are retained in the database for migration safety,
but cannot use the new phone login. Users must register with a username and
phone number.

## Virtual coins and history

- Admins can add or debit coins only when **both username and phone number
  match** an existing user. Debits cannot exceed the current balance. Every
  adjustment records the administrator, amount, and resulting balance in an
  append-only transaction history.
- Users can record virtual bets with a market, selection, and coin amount.
  The balance is debited atomically; users cannot spend more coins than they
  have. The wallet page shows the current balance and transaction/bet history.
- Coins have no cash value, cannot be redeemed or withdrawn, and this app does
  not process deposits, payments, or cash withdrawals. The KingStarline game
  uses virtual-points-only entries and virtual-points-only results.
  Requests to add or remove virtual coins and general support open WhatsApp
  to +91 8699915927. Coin requests include the user's username, phone, action,
  and amount; general support includes the user's account details. Messages
  are not sent automatically; users must review and send them, and admins must
  apply any approved coin adjustment manually in the admin page.

## KingStarline virtual game

The game is available at `/virtual-game`. New accounts start with zero virtual
points; an administrator must credit points before they can place entries.
Markets, five non-Sangam game types, panna suggestions, rates, the win
calculator, entry confirmation, and personal entry/result views use the `/api`
endpoints. Bet rates and limits are stored in the database, and each entry
snapshots its rate.
The admin page can create and edit market schedules and rates. Set
`RESULT_MODE=rng` (the default) for automatically generated results with
commitment/reveal verification, or `RESULT_MODE=admin` to enable manual Open
and Close result declaration; the scheduler does not generate results in admin
mode. Declaring a result settles entries that have become decidable.

Daily bonuses/refills and Half/Full Sangam are intentionally not included.
Virtual payouts are points only and are never cash or redeemable value.

## Caching and upstream traffic

- Public upstream pages and assets are cached in shared Redis. A Redis lock
  prevents concurrent app workers from fetching the same uncached page at once.
- A shared Redis token bucket caps all page and market fetches at
  `UPSTREAM_REQUESTS_PER_SECOND` across app workers. The default is an example,
  not an upstream-approved limit; set it within the source operator's published
  limit. Rate-limit exhaustion serves stale content or returns `503` with
  `Retry-After`.
- HTTP 403/429 and network/server failures open a shared backoff. The app does
  not rotate IPs, disguise requests, or retry around access controls. Use only
  an API and request rate you are authorized to use; resolve a 403 with the
  source operator, not by bypassing it.

## Production and capacity

The Compose file is a local development environment, not a production
deployment. A typical deployment needs an HTTPS CDN/WAF edge, private
autoscaled app instances, managed PostgreSQL with backups, separate managed
Redis resources, trusted ingress configuration, strong secrets, phone
verification, bot protections, and staged load testing. The application has
not been load-tested and does not guarantee a particular request rate or
availability.

## Native Android app

The Kotlin/Jetpack Compose client is in [android/README.md](android/README.md). It uses the existing FastAPI cookie-session and virtual-points APIs; profile editing, account recovery, and push notifications are not backend features and are not implemented. Production builds require an HTTPS API base URL supplied through a Gradle property.

## Tests

```powershell
py -m pip install -r .\requirements-dev.txt
py -m pytest
```
