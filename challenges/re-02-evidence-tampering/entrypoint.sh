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

# Read key from file or env; fallback handled in binary for offline use.
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE")"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
fi

# Copy compiled binary to shared challenge-files mount for download
if [ -d "/challenge-files/re-02-evidence-tampering" ]; then
  cp /app/evidence_tool /challenge-files/re-02-evidence-tampering/evidence_tool
  chmod 755 /challenge-files/re-02-evidence-tampering/evidence_tool || true
fi

exec /app/evidence_tool
