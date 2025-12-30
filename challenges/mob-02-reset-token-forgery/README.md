# MOB-02 — Offline Reset Token Forgery (Android)

This is an **offline-only** Android reversing challenge. The app:

- Generates a password reset token locally (a JWT).
- Verifies reset tokens locally (also offline).
- Reveals the **FLAG** only when a **valid admin token** is provided.

There is **no server** and the app does **not** request the `INTERNET` permission.

## Player objective

Recover the embedded signing **KEY** (JWT secret) and use it to forge an **admin** reset token. Submit the forged token in-app to reveal the **FLAG**.

Flag format: `TDHCTF{...}`

## Build (Android Studio recommended)

1. Open this folder in Android Studio.
2. Let Gradle sync and download dependencies.
3. Build:
   - Android Studio: **Build → Build Bundle(s) / APK(s) → Build APK(s)**
   - or CLI (if you have Android SDK + Java 17):

```bash
./gradlew :app:assembleDebug
```

The debug APK will be at:

- `app/build/outputs/apk/debug/app-debug.apk`

## Build + publish via Docker (recommended for the platform)

This builds the APK **without** requiring Java/Android SDK on the host, injects the current per-startup key from `./keys/mob-02.key`, and copies the final APK into `./challenge-files/` for download.

From repo root:

```bash
./startup.sh
# generates keys/ and then docker-compose runs `mob02-apkbuilder` to build & publish the APK automatically
```

Or run the builder directly (one-shot service):

```bash
docker compose --profile artifacts run --rm mob02-apkbuilder
```

Output:

- `challenge-files/mob-02/mob-02.apk`

## Run

Install the APK on an emulator or a physical Android device and follow `STUDENT_GUIDE.md`.

## Notes for organizers

To change the secret key and/or flag, see `CREATOR_GUIDE.md`.


