#!/bin/bash
set -e

: "${CTF_KEY:=REPLACE_ME_KEY}"
: "${CTF_FLAG:=REPLACE_ME_FLAG}"

# KEY: rio-only
printf "%s
" "$CTF_KEY" > /home/rio/mint.key
chown rio:rio /home/rio/mint.key
chmod 0400 /home/rio/mint.key

# FLAG: root-only
printf "%s
" "$CTF_FLAG" > /root/flag.txt
chown root:root /root/flag.txt
chmod 0400 /root/flag.txt

ssh-keygen -A >/dev/null 2>&1 || true

# Start cron (background)
service cron start >/dev/null 2>&1 || /usr/sbin/cron

exec /usr/sbin/sshd -D -e
