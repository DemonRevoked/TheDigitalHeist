#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user
STUDENT_USER="${STUDENT_USER:-nairobi}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@5}"

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
  export CHALLENGE_KEY="offline-default-crypto03"
fi

# Generate flag from key
export CHALLENGE_FLAG="TDHCTF{${CHALLENGE_KEY}}"

echo "[CRYPTO-03-QUANTUM-SAFE] Starting challenge setup..."
echo "[*] Using key: ${CHALLENGE_KEY:0:20}..."
echo "[*] Flag: ${CHALLENGE_FLAG:0:25}...}"

# Generate challenge files dynamically (this may take a while with 1337-bit primes)
echo "[*] Generating encrypted challenge file (may take 30-60 seconds)..."
sage /app/src/1337crypt.sage

# Copy challenge files to user home directory
USER_DIR="/home/${STUDENT_USER}/quantum-safe"
mkdir -p "$USER_DIR"
if [ -f "/challenge-files/crypto-03-quantum-safe/1337crypt_output.txt" ]; then
  cp /challenge-files/crypto-03-quantum-safe/1337crypt_output.txt "$USER_DIR/"
fi

# Add README with instructions
cat > "$USER_DIR/README.txt" << 'EOF'
=== CRYPTO-03: Quantum-Safe Vault ===

MISSION:
Break the advanced Goldwasser-Micali encryption in 1337crypt_output.txt

INTELLIGENCE:
- 1337-bit RSA primes (extremely large!)
- Goldwasser-Micali probabilistic encryption
- Encrypts flag bit-by-bit using quadratic residuosity
- Mathematical hint provided: hint = D * (√p + √q)

VULNERABILITY:
The hint leaks information about the prime factors!

ATTACK STRATEGY:
1. Use the hint to factor n:
   - Calculate s = hint / D
   - s = √p + √q
   - Use algebra: s² = p + q + 2√n
   - Solve quadratic equation with p*q = n

2. Decrypt each ciphertext bit using Legendre symbols:
   - legendre(c, p) = 1  →  bit is 0
   - legendre(c, p) = -1 →  bit is 1

3. Convert bits back to string to reveal flag

TOOLS NEEDED:
- SageMath (for advanced number theory)
- Deep understanding of:
  * RSA mathematics
  * Legendre symbols
  * Quadratic residuosity
  * Goldwasser-Micali encryption

OBJECTIVE:
Factor n, decrypt bit-by-bit to reveal: TDHCTF{...}

This is the ultimate crypto challenge. Good luck!
EOF

chown -R "${STUDENT_USER}:${STUDENT_USER}" "$USER_DIR"
chmod 700 "/home/${STUDENT_USER}"
chmod 644 "$USER_DIR"/*

echo "[+] Challenge files copied to /home/${STUDENT_USER}/quantum-safe/"
echo "[+] Challenge setup complete!"

# Start SSH and keep container running
/usr/sbin/sshd -D

