# Student Guide — Rio’s Radio Relay Node (Hard)

## Story context
Rio’s relay node keeps crew communications alive while the Mint rotates access material on schedule. The Professor suspects the relay operations pipeline can be abused: first to pivot into a service account, then to reach the vault.

## Your objectives
Recover **two artifacts**:

1. **KEY** — `/home/rio/mint.key` (readable only by the `rio` account)  
2. **FLAG** — `/root/flag.txt` (root-only)

Submit **both** values to complete the challenge.

## Access
- **SSH username:** `tokyo`  
- **SSH password:** `tokyo123`  
- **SSH host:** `localhost`  
- **SSH port:** `2227`

Example:
```bash
ssh tokyo@localhost -p 2227
```

## Rules of engagement
- This is a **system exploitation** exercise; no web exploitation is required.
- Do not run destructive or noisy actions that break the environment for others.
- Expect a **multi-step chain**: pivot → escalate → retrieve artifacts.

## What you are given
- A standard Ubuntu shell as a low-privilege user.
- Relay and rotation components on the host.
- Logs and config files that may contain clues.

## What “success” looks like
- You can read `/home/rio/mint.key` (KEY).
- You can read `/root/flag.txt` (FLAG).

## Recommended workflow (non-spoiler)
1. **Baseline enumeration**
   - Identify users on the system and their roles.
   - Check running services, scheduled tasks, and writable paths.
2. **Find the relay footprint**
   - Look for directories under `/opt` and logs under `/var/log`.
   - Identify relay-related configuration files.
3. **Pivot to the relay operator**
   - Determine how the service account is accessed and whether credentials are mishandled.
4. **Find root automation**
   - Identify what runs periodically as root (cron jobs).
   - Inspect what files it reads and whether any of those are writable by non-root accounts.
5. **Escalate**
   - Use the operational weakness to gain root access sufficient to read the FLAG.

## Hints ladder (use only if stuck)
**Hint 1:** The relay footprint is not hidden; check `/opt` and `/var/log`.  
**Hint 2:** KEY is `rio`-only; you must become `rio` to read it.  
**Hint 3:** Look for periodic execution (cron) and which files those scripts *source* or read.  
**Hint 4:** If a root process reads configuration from a writable location, that is usually the pivot point.

## Submission checklist
- KEY value (exact string from `/home/rio/mint.key`)
- FLAG value (exact string from `/root/flag.txt`)
