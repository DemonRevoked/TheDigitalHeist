# Creator Guide — Berlin’s Locker Controller (Medium)

## Summary
- **Category:** System exploitation (local privilege escalation)
- **Theme:** Money Heist (Berlin / Mint staging)
- **Player entry:** SSH credentials
- **Artifacts:** KEY + FLAG
- **Primary weakness:** A **SUID-root** utility executes a helper program using PATH resolution.

## Files and artifacts (in-container)
- Player user: `tokyo` (password `tokyo123`)
- SUID binary: `/usr/local/bin/lockerctl` (mode `4755`, owner `root:root`)
- Intended helper: `/usr/local/sbin/backup`
- KEY: `/opt/mint/key.txt` (`root:lockers`, mode `0440`)
- FLAG: `/root/flag.txt` (`root:root`, mode `0400`)

## Secret injection (no hardcoding)
Secrets are **not** embedded into image layers. They are generated at container startup by `entrypoint.sh`:

- `CTF_KEY` → `/opt/mint/key.txt`
- `CTF_FLAG` → `/root/flag.txt`

### Recommended deployment pattern
1. Set per-instance values (environment or repo `.env`):
   - `EXP01_KEY=...`
   - `EXP01_FLAG=...`
2. Deploy (from repo root):
```bash
docker compose up --build -d exp01-berlinslocker
```

## Intended solve outline (high-level)
1. Player enumerates for privilege boundaries (SUID/SGID binaries).
2. Player identifies `lockerctl` runs with elevated privileges.
3. Player inspects how `lockerctl` performs its work and discovers it launches an external helper by **name**, not absolute path.
4. Player leverages PATH resolution to run a controlled helper under elevated privileges, enabling reading KEY and FLAG.

(Do not include command-by-command instructions in student materials; keep those internal.)

## Validation steps (creator)
Use these to ensure the target behaves correctly **before** releasing:

### Container health
- Container starts cleanly and exposes SSH:
  - host port `2221` -> container port `22`

### Permissions
From a shell inside the container:
- `ls -l /usr/local/bin/lockerctl` shows `-rwsr-xr-x` (SUID set)
- `ls -l /opt/mint/key.txt` shows `-r--r----- root lockers`
- `ls -l /root/flag.txt` shows `-r-------- root root`

### Access control sanity
- As `tokyo`, reading KEY/FLAG should fail initially.
- After completing the intended privesc, both should be readable.

## Difficulty tuning
If you need to tune difficulty without changing the core lesson:
- **Easier:** add a brief note in `/var/log/lockerctl/lockerctl.log` about how the helper is invoked.
- **Harder:** remove explicit helper name references from logs; keep only the binary behavior.

## Reset and reissue
- To rotate secrets: update `.env` and restart the container.
- To reset filesystem state: redeploy the container (stateless except runtime-generated secrets).

## Safety and isolation notes
- This container intentionally includes unsafe configurations.
- Deploy only in isolated environments dedicated to training/CTF.
- Keep the host patched and do not run privileged Docker unless required by your platform.
