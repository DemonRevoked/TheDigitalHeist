# Creator Guide — MOB-02 Offline Reset Token Forgery

This challenge is intentionally vulnerable because the app performs **client-side JWT verification** using an embedded secret. Players extract the secret and forge an admin token.

## What to customize

- **JWT secret (KEY)**: assembled in `SecretProvider`.
- **FLAG**: stored as plaintext in `FlagVault` (jadx-visible; allowed to hardcode flags).

## Changing the KEY (JWT secret)

1. Edit the secret parts in `SecretProvider`.
2. Re-generate the encrypted flag blob (next section).
3. Build a new APK.

## Changing the FLAG

Edit `FlagVault.FLAG` directly.

### Current defaults (as shipped)

- JWT signing secret string (exact): `TDH_MOB03_RESET_TOKEN_SIGNING_KEY_2025`
- Flag plaintext: `TDHCTF{offline_reset_token_forgery}`
- Challenge key: injected at build time from `./keys/mob-02.key` into `BuildConfig.MOB02_CHALLENGE_KEY`

## Build

```bash
./gradlew :app:assembleDebug
```

## Platform build (Docker, dynamic per-startup key)

The platform generates a new key each startup at `./keys/mob-02.key`. The APK must embed that value at build time.

Run:

```bash
docker compose --profile artifacts run --rm mob02-apkbuilder
```

This will:
- read `./keys/mob-02.key`
- build the APK in Docker
- publish to `./challenge-files/mob-02/mob-02.apk`

## Security notes (what is “secure” here)

Within the intended design:

- Token verification is correct (signature + exp checks).
- The app is offline-only (no `INTERNET` permission).
- The flag is not plaintext in resources (must be decrypted after successful authorization).

The intentional flaw is **trusting client-side verification** for an authorization decision.


