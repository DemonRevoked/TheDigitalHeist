# Student Guide — Berlin’s Locker Controller (Medium)

## Story context
Berlin’s “Locker Controller” rotates Mint staging logs so the crew can track movements without leaving traces. It runs with elevated privileges because it touches protected locations. The Professor believes the tool can be abused.

## Your objectives
You must recover **two artifacts**:

1. **KEY** — `/opt/mint/key.txt`  
2. **FLAG** — `/root/flag.txt`

Submit **both** values to complete the challenge.

## Access
The target is an isolated Docker-hosted system exposed via SSH.

- **SSH username:** `tokyo`  
- **SSH password:** `tokyo123`  
- **SSH host:** `localhost`  
- **SSH port:** `2221`

Example:
```bash
ssh tokyo@localhost -p 2221
```

## Rules of engagement
- This is a **system exploitation** exercise. No web application attacks are required.
- Do not attack any machine other than this target container.
- Do not attempt denial-of-service or destructive actions that break the target for others.
- Your goal is to **escalate privileges** and retrieve the two artifacts.

## What you are given
- A standard Ubuntu user environment.
- A Mint “locker” tool installed on the system.
- Logs and story clues in standard system locations.

## What “success” looks like
- You can read `/opt/mint/key.txt` (KEY).
- You can read `/root/flag.txt` (FLAG).

## Recommended workflow (non-spoiler)
1. **Baseline enumeration**
   - Identify your user, groups, and current privileges.
   - Look for unusual binaries, scheduled jobs, and file permissions.
2. **Locate the “locker controller”**
   - Find its install path and how it is intended to be used.
   - Identify whether it runs with elevated privileges.
3. **Understand its behavior**
   - Check what external programs it calls.
   - Note whether it uses absolute paths or relies on the environment.
4. **Privilege escalation**
   - Use the weakness you discovered to obtain access sufficient to read the KEY and FLAG.

## Hints ladder (use only if stuck)
**Hint 1:** Not everything interesting is in `/home`. Check `/usr/local/bin` and `/opt`.  
**Hint 2:** Look for binaries with special permission bits (SUID/SGID).  
**Hint 3:** If a privileged program runs another program by name (not full path), think about how the OS decides what gets executed.  
**Hint 4:** Re-check your environment variables and how they influence command resolution.

## Submission checklist
- KEY value (exact string from `/opt/mint/key.txt`)
- FLAG value (exact string from `/root/flag.txt`)
