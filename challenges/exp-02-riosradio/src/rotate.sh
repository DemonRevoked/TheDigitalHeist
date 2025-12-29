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
