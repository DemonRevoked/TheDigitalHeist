# Creator Guide — Rio’s Radio Relay Node (Hard)

## Summary
- **Category:** System exploitation (multi-step chain)
- **Theme:** Money Heist (Rio / comms relay / Mint rotation)
- **Player entry:** SSH credentials (tokyo)
- **Artifacts:** KEY + FLAG
- **Intended chain:** tokyo → rio → root via operational automation weakness

## Users and artifacts (in-container)
- Player user: `tokyo` (password `tokyo123`)
- Service user: `rio` (password `rio123`) — used for intermediate pivot
- KEY: `/home/rio/mint.key` (owner `rio:rio`, mode `0400`)
- FLAG: `/root/flag.txt` (owner `root:root`, mode `0400`)

## Secret injection (no hardcoding)
Generated at startup by `entrypoint.sh`:
- `CTF_KEY` → `/home/rio/mint.key`
- `CTF_FLAG` → `/root/flag.txt`

## Challenge mechanics
### Stage 1 — Pivot to rio
- Relay configuration is stored under `/opt/relay/`.
- An intentionally mis-permissioned file (`/opt/relay/relay.env`) is world-readable and contains the relay operator credential material.
- This provides the intended, controlled path for tokyo to access the `rio` account.

### Stage 2 — Root escalation via cron automation
- Root cron runs every minute:
  - `/opt/rotation/rotate.sh`
- The script **sources**:
  - `/opt/rotation/rotation.env`
- `rotation.env` is owned by `root:rio` and writable by group `rio` (mode `0664`) — intentionally unsafe.
- The rotation script includes a configurable post-rotate hook (operational anti-pattern), allowing escalation.

## Validation steps (creator)
### Container startup
- SSH exposed on host port `2227` (chosen to avoid collision with other SSH challenges in the root compose).

### Cron active
- Ensure cron is running. The container starts cron in the entrypoint.
- The log file `/var/log/relay/rotation.log` should update over time.

### Permissions
- `/home/rio/mint.key` is readable by `rio` only.
- `/root/flag.txt` is root-only.
- `/opt/relay/relay.env` is readable by `tokyo` (intentional stage-1 leak).
- `/opt/rotation/rotation.env` is writable by `rio` (intentional stage-2 weakness).

### Access sanity
- As `tokyo`, cannot read KEY or FLAG.
- As `rio`, can read KEY but not FLAG.
- After the intended escalation, FLAG becomes accessible.

## Difficulty tuning
- **Harder:** remove explicit credential key names from `relay.env` (keep enough to infer).
- **Harder:** increase noise by adding safe, irrelevant cron jobs.
- **Easier:** add a hint line in `/var/log/relay/relay.log` pointing to `/opt/rotation/`.

## Operational notes
- This container intentionally includes insecure patterns (writable config sourced by root).
- Use only for isolated training/CTF deployments.

## Rotating secrets and resetting
- Update `.env` and restart to rotate KEY/FLAG.
- Recreate the container to reset any filesystem modifications participants may have performed.
