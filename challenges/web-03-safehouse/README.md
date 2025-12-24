# Challenge 3 (Hard) — La Casa de Papel: SSRF Filter Bypass + Internal Service Pivot

## 🎭 Storyline
You are part of the Money Heist crew. The Professor has hidden the escape route coordinates in a secure hidden vault server. Your mission: bypass the security protocols and retrieve the coordinates using the Network Scanner reconnaissance system.

## What players should learn
- SSRF in "URL preview" features
- Naive allowlist and parsing mistakes (userinfo `@` trick)
- Pivoting to an internal-only service on the Docker network

## Services
- web (public) — Node.js/Express (Safe House Network)
- internal-admin (private) — Professor's Hidden Vault Server (not published to host)

## Run
1. Copy `.env.example` to `.env` (optional edits).
2. Start:
   ```bash
   docker compose up --build
   ```
3. Open:
   - http://localhost:5003

## Intended solve (high level)
1. Login as `tokyo/tokyo123` (or `alice/alice123` for backward compatibility).
2. Access the Base Camp to find the Professor's security key.
3. Use the Network Scanner SSRF to access the hidden vault server using an allowlist bypass:
   - the validator checks the *string* for an allowlisted domain, but the actual URL host is after `@`.
4. Use the security key to retrieve the escape route coordinates (flag) from the Professor's hidden vault server via SSRF.

## Creator notes
- SSRF is in `src/routes/preview.js`.
- Internal service runs at `http://internal-admin:8080/` on the Docker network only.
- Money Heist themed for engaging storyline.
