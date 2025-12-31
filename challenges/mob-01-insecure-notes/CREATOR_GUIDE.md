# Creator Guide — MOB-01 Insecure Notes (Offline APK)

## What this challenge teaches
- Basic APK decompilation (jadx)
- Finding **hardcoded secrets** / weak local checks
- Understanding why client-side “auth” is not real security

## Dynamic challenge key (KEY)
`startup.sh` generates a new per-startup key at:
- `./keys/mob-01.key`

At build time, the APK embeds it into:
- `BuildConfig.MOB01_CHALLENGE_KEY`

This is the **KEY output** shown to students after success.

## Flag (embedded)
The FLAG is embedded as a **plaintext constant** inside `FlagVault` so it is trivially discoverable via jadx (intentionally easy).

## Access phrase (student input)
Students must find and enter this exact phrase (embedded in-app):
- `MINT-ACCESS-7429-PROFESSOR`

## Build & publish

```bash
docker compose --profile artifacts run --rm mob01-apkbuilder
```

Output:
- `./challenge-files/mob-01/mob-01.apk`
