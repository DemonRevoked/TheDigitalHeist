# Money Heist System Exploitation CTF (Medium)
## Berlin’s Locker Controller — SUID PATH Hijack

This is a **system exploitation** challenge delivered as a **Docker SSH container**.

### Player objective
Retrieve **both**:
- **KEY**  : `/opt/mint/key.txt`
- **FLAG** : `/root/flag.txt`

Both are generated at container start from environment variables `CTF_KEY` and `CTF_FLAG`.

### SSH access
Default creds (change in `Dockerfile` if needed):
- `tokyo / tokyo123`

### Run
1. Copy `.env.example` -> `.env` and set values:
   - `CTF_KEY=...`
   - `CTF_FLAG=...`
2. Start:
```bash
docker compose up --build
```
3. SSH:
```bash
ssh tokyo@localhost -p 2221
```

### Validation
To verify the CTF is working correctly, run the validation script:
```bash
./run_validation.sh
```
This will automatically execute the exploit and display the KEY and FLAG values.

### Notes for creators
- This container is intended for isolated lab/CTF use.
- Root login via SSH is disabled.
