# Student Guide — MOB-02 Offline Reset Token Forgery

## What you get

- An Android APK (offline; no server).
- The app can generate a “reset token” and accepts a token to reveal the flag.

## Objective

Reveal the flag by submitting a **valid admin token**.

## Suggested tools

- `jadx` (APK decompiler)
- Any JWT tooling (offline) to re-sign a token once you have the key

## Intended path (high level)

1. Install and open the APK.
2. Use the **Generate Token** section to mint a reset token for any email.
3. Recognize the token format (JWT): `header.payload.signature`.
4. Decompile the APK with `jadx`.
5. Find the code that verifies tokens and extract the embedded signing key (secret).
6. Forge a new token:
   - Same algorithm
   - Set `role` to `admin`
   - Keep `exp` in the future
   - Sign with the extracted secret
7. Paste your forged token into the **Submit Token** section.
8. If valid, the app reveals the flag.

## Hint ladder

1. The token has three dot-separated parts.
2. Look for token verification logic in the app code.
3. If the app verifies tokens locally, it must have everything it needs.
4. Once you can sign your own token, try changing the role claim.


