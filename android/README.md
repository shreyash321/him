# DhanRAJ Android app

Native Kotlin/Jetpack Compose client for the FastAPI application in the parent directory. The repository did not contain an Android Studio starter, so this is a new `android/` project; it uses the backend's existing cookie-session APIs and does not add backend endpoints.

## Run

- Open this folder in Android Studio (JDK 17 and Android SDK 35 required), sync Gradle, then run the `app` configuration on an emulator.
- The debug base URL is `http://10.0.2.2:8000/` for the Android emulator talking to a backend on the host. A physical device needs a reachable development host URL; use HTTPS, or allow that development host in the debug-only `app/src/debug/res/xml/network_security_config.xml` before using cleartext HTTP.
- Production API URL is injected at build time, never embedded as a credential. Build a release APK with `-PDHANRAJ_API_BASE_URL=https://your-deployed-api/`; release APK tasks reject a missing or non-HTTPS URL. The backend must be deployed with HTTPS and allow the app's same-origin `Origin` header checks.

## Backend-supported behavior

Login, registration, session restore/logout, read-only account details, wallet transaction history, markets, round state, bet types, virtual-point entries, entry history, and results use routes found in `app/auth.py`, `app/wallet.py`, and `app/games.py`. Cookies (including the CSRF cookie) are persisted with AndroidX encrypted preferences. Passwords are sent only to the backend over the configured connection and are never saved locally.

Profile editing, password recovery, push notifications, and notification preferences do not exist in the backend and are not represented as working features. Coin values are nonredeemable virtual points only; the app does not accept deposits or provide cash payouts.

## Build outputs

Debug APK: `app/build/outputs/apk/debug/app-debug.apk`. Install it on a connected device/emulator with Android platform tools using `adb install -r app/build/outputs/apk/debug/app-debug.apk`. Release signing is intentionally not configured; use Android Studio's signed APK wizard or provide signing values via a local, ignored Gradle properties file/CI secrets. Never commit signing keys or passwords.