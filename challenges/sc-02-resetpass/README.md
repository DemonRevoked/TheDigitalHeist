# Money Heist Secure Coding CTF (Medium)
## Mission: Mint Access Badge Reset Flow — Secure Reset Implementation

**Goal:** Patch the password reset implementation to meet secure coding requirements.

---

## 📚 Student Resources

**⭐ START HERE:**
- 📖 **[STUDENT_WALKTHROUGH.md](STUDENT_WALKTHROUGH.md)** - Complete step-by-step guide with solution code included

The walkthrough includes:
- Detailed explanation of vulnerabilities
- Complete secure solution code (ready to copy/paste)
- Step-by-step instructions for web-based and file-based access
- Testing instructions
- Troubleshooting guide
- Security concepts explained

---

## CTF Structure (Two Parts)

### Part 1: Get the KEY
When your implementation is correct, you can fetch the key from:
- `GET /mint/key`

The server unlocks `/mint/key` only if its **startup self-check** confirms the reset flow is secure.

### Part 2: Get the FLAG
Once you have the KEY, use it to fetch the flag:
- `GET /mint/flag?key=YOUR_KEY`
- `POST /mint/flag` with `key=YOUR_KEY` in the body

The flag endpoint validates the key and returns the flag if correct.
**Note:** The key is provided by the deployment via environment/secret-file configuration.

---

## Run (server)
1. Copy `.env.example` → `.env` (optional edits)
2. Start:
   ```bash
   # from repo root
   docker compose up --build sc02-resetpass
   ```
   Or without Docker:
   ```bash
   npm install
   npm start
   ```
3. Open:
   - http://localhost:5102

## Run (tests)
```bash
# from repo root
docker compose run --rm sc02-resetpass npm test
```
Or without Docker:
```bash
npm test
```

---

## Default demo user
- Email: `tokyo@mint.local`
- Password: `tokyo123`

## Environment Variables

Default values (set in `.env` or environment):
- `KEY`: Challenge KEY required by `/mint/flag` (default: `mint-key-secret`)
  - Can also be provided via `KEY_FILE` (file contents are used as the key)
  - Backward compatible: `KEY_SECRET` / `KEY_SECRET_FILE` are also accepted as inputs for the key
- `FLAG`: The flag returned by `/mint/flag` when provided with correct key
  - This is the same flag for all students

## What to fix
Primary file:
- `src/security/reset.js`

Secure coding requirements:
- Token generation uses `crypto.randomBytes(32)` and hex encoding (64 chars)
- Store only a **hash** of the token (not the raw token)
- Token expires (15 minutes)
- One-time use: token invalidated after successful reset
- Use constant-time comparison for hashes
- Forgot-password response does **not** reveal whether email exists

**Important:** The tests and startup self-check expect the forgot-password message to be exactly:
`If the account exists, reset instructions have been issued.`

**See [STUDENT_WALKTHROUGH.md](STUDENT_WALKTHROUGH.md) for complete solution and detailed instructions.**
