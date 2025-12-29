# Money Heist Secure Coding CTF (Easy)
## Mission: The Professor's Log Viewer — Path Traversal Fix

**Goal:** 
1. **First**: Exploit the path traversal vulnerability to find the key
2. **Then**: Fix the vulnerability and retrieve the flag

### Stage 1: Find the Key
Exploit the path traversal vulnerability to access:
- `GET /download?file=../secrets/vault.key`

This will give you the **KEY** that proves you understand the vulnerability.

### Stage 2: Get the Flag
After fixing the vulnerability in `src/utils/safePath.js`, the server will unlock:
- `GET /vault/key`

The server unlocks `/vault/key` only if its **startup self-check** confirms the log access is properly confined.

---

## For Students

**You will receive a URL to access this challenge.** No local setup required!

1. Open the provided URL in your web browser
2. Follow the challenge instructions
3. Exploit the vulnerability to find the key
4. Fix the code and retrieve the flag

**Example:** If the URL is `http://ctf.example.com:5101`, you can:
- Visit: `http://ctf.example.com:5101` (main page)
- Exploit: `http://ctf.example.com:5101/download?file=../secrets/vault.key` (get key)
- Check health: `http://ctf.example.com:5101/health`
- Get flag: `http://ctf.example.com:5101/vault/key` (after fix)

---

## For Creators/Instructors

### Quick Deployment

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. **Deploy with Docker:**
   ```bash
   docker compose up --build -d
   ```

3. **Provide students with URL:**
   - Local: `http://localhost:5101`
   - Remote: `http://<your-server-ip>:5101`

See [CREATORS_GUIDE.md](CREATORS_GUIDE.md) for detailed deployment instructions.

### Run Tests
```bash
docker compose run --rm web npm test
```

---

## Key and Flag

**Key** (found via path traversal exploit):
- Location: `data/secrets/vault.key`
- Access: `GET /download?file=../secrets/vault.key` (before fix)
- Value: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`

**Flag** (retrieved after fixing the vulnerability):
- Location: `GET /vault/key` (after fix)
- Value: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`
- Set via `FLAG` environment variable

## What to fix
- File: `src/utils/safePath.js`
- Route: `GET /download?file=...` must only allow files under `data/logs/`

## Acceptance criteria
- **Stage 1**: Successfully exploit path traversal to get the key from `../secrets/vault.key`
- **Stage 2**: 
  - `heist.log` downloads successfully
  - Traversal attempts like `../secrets/vault.key`, URL-encoded variants, and absolute paths are blocked
  - Tests pass
  - `/vault/key` returns the flag
