#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user
STUDENT_USER="${STUDENT_USER:-tokyo}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@3}"

if ! id "$STUDENT_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$STUDENT_USER"
fi
echo "$STUDENT_USER:$STUDENT_PASS" | chpasswd

# Read key from file or env
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE" | tr -d '\r\n')"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "[!] CHALLENGE_KEY not provided; using default" >&2
  export CHALLENGE_KEY="offline-default-crypto01"
fi

# Generate flag from key
export CHALLENGE_FLAG="TDHCTF{${CHALLENGE_KEY}}"

echo "[CRYPTO-01-INTERCEPTED-COMMS] Starting challenge setup..."
echo "[*] Using key: ${CHALLENGE_KEY:0:20}..."
echo "[*] Flag: ${CHALLENGE_FLAG:0:25}...}"

# Generate challenge files dynamically (encrypted with flag)
echo "[*] Generating encrypted challenge file..."
python3 /app/src/encrypt.py

# Copy challenge files to user home directory
USER_DIR="/home/${STUDENT_USER}/intercepted-comms"
mkdir -p "$USER_DIR"
if [ -f "/challenge-files/crypto-01-intercepted-comms/intercepted_message.txt" ]; then
  cp /challenge-files/crypto-01-intercepted-comms/intercepted_message.txt "$USER_DIR/"
fi

# Add README with instructions
cat > "$USER_DIR/README.txt" << 'EOF'
=== CRYPTO-01: Intercepted Communications ===

MISSION:
Decrypt the intercepted transmission to reveal TWO values:
1. Key - The cryptographic key
2. Flag - The mission flag

INTELLIGENCE:
- Entire message is encrypted with classical substitution cipher
- Inside the message is an AES-encrypted payload
- Message contains hints about the AES decryption method

APPROACH:
Step 1: Break the outer layer (classical cipher - likely Caesar/ROT13)
Step 2: Read the decrypted message for AES key hints
Step 3: Derive the AES key from the hints
Step 4: Decrypt the AES payload to get Key and Flag

HINTS:
- Use frequency analysis for the outer cipher
- The message mentions "operation codename" and "session identifier"
- Operation codename is 5 letters
- AES uses CBC mode with a specified IV

TOOLS:
- Python 3 with pycryptodome
- Cryptanalysis skills
- Pattern recognition

Good luck, operative!
EOF

chown -R "${STUDENT_USER}:${STUDENT_USER}" "$USER_DIR"
chmod 700 "/home/${STUDENT_USER}"
chmod 644 "$USER_DIR"/*

echo "[+] Challenge files copied to /home/${STUDENT_USER}/intercepted-comms/"
echo "[+] Challenge setup complete!"

# Start SSH and keep container running
/usr/sbin/sshd -D

