# MOB-01 — Insecure Notes (Android, Offline)

This is an **offline-only** Android reversing challenge (easy).

- No server, no endpoints.
- The app has a “locked note” protected by an intentionally weak, client-side PIN check.
- On success it reveals:
  - **KEY** (per-startup challenge key, injected at build time)
  - **FLAG** (plaintext in-app)

## Build + publish (platform)

The platform generates `./keys/mob-01.key` each startup. The APK must embed that value at build time.

Run:

```bash
docker compose --profile artifacts run --rm mob01-apkbuilder
```

Output:
- `challenge-files/mob-01/mob-01.apk`

## Run
Install the APK and follow `STUDENT_GUIDE.md`.
