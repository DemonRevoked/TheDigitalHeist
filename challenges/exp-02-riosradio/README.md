# Money Heist System Exploitation CTF (Hard)
## Rio’s Radio Relay Node — Pivot + Root Automation Abuse

This is a **system exploitation** challenge delivered as a **Docker SSH container**.

### Player objective
Retrieve **both**:
- **KEY**  : `/home/rio/mint.key`  (rio-only)
- **FLAG** : `/root/flag.txt`      (root-only)

Both are generated at container start from environment variables `CTF_KEY` and `CTF_FLAG`.

### SSH access
Default creds (change in `Dockerfile` if needed):
- `tokyo / tokyo123`

### Run
1. Set values (environment or repo `.env`):
   - `EXP02_KEY=...`
   - `EXP02_FLAG=...`
2. Start (from repo root):
```bash
docker compose up --build exp02-riosradio
```
3. SSH:
```bash
ssh tokyo@localhost -p 2227
```

### Notes for creators
- Root login via SSH is disabled.
- This container runs `cron` to simulate operational automation.
- Intended progression: tokyo -> rio -> root.
