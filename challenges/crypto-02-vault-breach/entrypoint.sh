#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user
STUDENT_USER="${STUDENT_USER:-berlin}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@4}"

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
  export CHALLENGE_KEY="offline-default-crypto02"
fi

echo "[CRYPTO-02-VAULT-BREACH] Starting challenge setup..."
echo "[*] Using key: ${CHALLENGE_KEY:0:20}..."
echo "[*] Flag: TDHCTF{vault_breach_decrypted}"

# Generate challenge files dynamically (encrypted with flag)
echo "[*] Generating encrypted challenge file..."
python3 /app/src/encrypt.py

# Copy challenge files to user home directory
USER_DIR="/home/${STUDENT_USER}/vault-breach"
mkdir -p "$USER_DIR"
if [ -f "/challenge-files/crypto-02-vault-breach/encrypted_vault.txt" ]; then
  cp /challenge-files/crypto-02-vault-breach/encrypted_vault.txt "$USER_DIR/"
fi

# Add README with instructions
cat > "$USER_DIR/README.txt" << 'EOF'
=== CRYPTO-02: Vault Breach ===

MISSION:
Break the RSA encryption in encrypted_vault.txt to reveal TWO values:
1. Key - The cryptographic key
2. Flag - The mission flag

INTELLIGENCE:
- Standard RSA encryption (1024-bit modulus)
- Public key (n, e) provided
- Encrypted message (c) provided
- VULNERABILITY: The prime numbers used are poorly chosen

HINTS:
- When two primes are too close, factorization becomes easier
- Research "Fermat's factorization method"
- Once you factor n, standard RSA decryption applies
- The decrypted message will contain both the key and flag separately

TOOLS NEEDED:
- Python 3 with pycryptodome
- Understanding of RSA mathematics
- Fermat's factorization algorithm

OBJECTIVE:
Factor n, calculate private key, decrypt to reveal both the key and flag.

Good luck!
EOF

chown -R "${STUDENT_USER}:${STUDENT_USER}" "$USER_DIR"
chmod 700 "/home/${STUDENT_USER}"
chmod 644 "$USER_DIR"/*

echo "[+] Challenge files copied to /home/${STUDENT_USER}/vault-breach/"
echo "[+] Challenge setup complete!"

# Start SSH and keep container running
/usr/sbin/sshd -D

