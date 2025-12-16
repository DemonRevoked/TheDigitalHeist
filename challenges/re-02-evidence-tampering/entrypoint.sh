#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user (storyline-friendly)
STUDENT_USER="${STUDENT_USER:-denver}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@2}"

if ! id "$STUDENT_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$STUDENT_USER"
fi
echo "$STUDENT_USER:$STUDENT_PASS" | chpasswd

# Start sshd
/usr/sbin/sshd

# Read key from file or env; no local generation here.
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE")"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "CHALLENGE_KEY not provided; set CHALLENGE_KEY or mount CHALLENGE_KEY_FILE." >&2
  exit 1
fi

exec /app/evidence_tool
