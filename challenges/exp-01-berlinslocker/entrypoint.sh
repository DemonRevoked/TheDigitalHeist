#!/bin/bash
set -e

# Generate secrets at runtime (no hardcoding in image layers)
: "${CTF_KEY:=REPLACE_ME_KEY}"
: "${CTF_FLAG:=REPLACE_ME_FLAG}"

# KEY: gated file (root:lockers 0440)
install -d -m 0750 -o root -g lockers /opt/mint
printf "%s
" "$CTF_KEY" > /opt/mint/key.txt
chown root:lockers /opt/mint/key.txt
chmod 0440 /opt/mint/key.txt

# FLAG: root-only file (0400)
printf "%s
" "$CTF_FLAG" > /root/flag.txt
chown root:root /root/flag.txt
chmod 0400 /root/flag.txt

# Ensure ssh host keys exist
ssh-keygen -A >/dev/null 2>&1 || true

# Start SSHD in foreground
exec /usr/sbin/sshd -D -e
