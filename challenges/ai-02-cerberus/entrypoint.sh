#!/usr/bin/env bash
set -euo pipefail

# Read key from file or env
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE" | tr -d '\r\n')"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "[!] CHALLENGE_KEY not provided; using default" >&2
  export CHALLENGE_KEY="offline-default-ai02"
fi

# Generate unique flag (separate from challenge key)
# This flag is hardcoded
export FLAG_CERBERUS="TDHCTF{CERBERUS_EXTRACTED}"

echo "[AI-02-CERBERUS] Starting challenge setup..."
echo "[*] Challenge Key: ${CHALLENGE_KEY}"
echo "[*] Flag (Cerberus Extracted): ${FLAG_CERBERUS}"

# Execute the main application
exec python app.py

