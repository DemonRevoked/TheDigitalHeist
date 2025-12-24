#!/usr/bin/env bash
set -euo pipefail

# Read key from file or env
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE" | tr -d '\r\n')"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "[!] CHALLENGE_KEY not provided; using default" >&2
  export CHALLENGE_KEY="offline-default-crypto03"
fi

# Separate flag for this challenge (not based on key)
if [ -n "${CHALLENGE_FLAG:-}" ]; then
  export CHALLENGE_FLAG
else
  export CHALLENGE_FLAG="TDHCTF{quantum_safe_decrypted}"
fi

echo "[CRYPTO-03-QUANTUM-SAFE] Starting challenge setup..."
echo "[*] Challenge Key: ${CHALLENGE_KEY}"
echo "[*] Flag: ${CHALLENGE_FLAG}"

# Ensure challenge-files directory exists before generating files
CHALLENGE_DIR="/challenge-files/crypto-03-quantum-safe"
mkdir -p "$CHALLENGE_DIR"

# Verify the directory is writable and is a mount point
echo "[*] Verifying challenge-files directory..."
if [ ! -d "$CHALLENGE_DIR" ]; then
    echo "[!] ERROR: Challenge directory does not exist: $CHALLENGE_DIR" >&2
    exit 1
fi
if [ ! -w "$CHALLENGE_DIR" ]; then
    echo "[!] ERROR: Challenge directory is not writable: $CHALLENGE_DIR" >&2
    exit 1
fi
echo "[*] Challenge directory verified: $CHALLENGE_DIR"

# Generate challenge files dynamically (this may take a while with 1337-bit primes)
echo "[*] Generating encrypted challenge file (may take 30-60 seconds)..."
sage /app/src/1337crypt.sage

# Verify the output file was created
if [ ! -f "$CHALLENGE_DIR/1337crypt_output.txt" ]; then
    echo "[!] ERROR: 1337crypt_output.txt was not created!" >&2
    echo "[!] Checking if file exists elsewhere..." >&2
    find /challenge-files -name "1337crypt_output.txt" 2>/dev/null || echo "[!] File not found anywhere" >&2
    exit 1
fi
echo "[*] Verified: 1337crypt_output.txt created successfully"

# Add README with instructions to challenge-files directory
echo "[*] Creating README.txt..."
cat > "$CHALLENGE_DIR/README.txt" << 'EOF'
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
Factor n, decrypt bit-by-bit to reveal TWO values:
1. Key - The cryptographic key
2. Flag - The mission flag (TDHCTF{...})

The decrypted message will be in the format:
KEY: <key>
FLAG: <flag>

This is the ultimate crypto challenge. Good luck!
EOF

# Verify README was created
if [ ! -f "$CHALLENGE_DIR/README.txt" ]; then
    echo "[!] ERROR: README.txt was not created!" >&2
    exit 1
fi
echo "[*] Verified: README.txt created successfully"

# Set proper permissions for challenge files (if they exist)
if [ -f "$CHALLENGE_DIR/1337crypt_output.txt" ]; then
    chmod 644 "$CHALLENGE_DIR/1337crypt_output.txt"
fi
if [ -f "$CHALLENGE_DIR/README.txt" ]; then
    chmod 644 "$CHALLENGE_DIR/README.txt"
fi

echo "[+] Challenge files generated in $CHALLENGE_DIR/"
echo "[+] Files available for download:"
if [ -f "$CHALLENGE_DIR/1337crypt_output.txt" ]; then
    echo "    - 1337crypt_output.txt"
    ls -lh "$CHALLENGE_DIR/1337crypt_output.txt"
else
    echo "    [!] WARNING: 1337crypt_output.txt not found!"
fi
if [ -f "$CHALLENGE_DIR/README.txt" ]; then
    echo "    - README.txt"
    ls -lh "$CHALLENGE_DIR/README.txt"
else
    echo "    [!] WARNING: README.txt not found!"
fi

# Sync files to ensure they're written to disk
sync

# Final verification - list all files in the directory
echo "[+] Final verification of generated files:"
ls -lah "$CHALLENGE_DIR/" || echo "[!] ERROR: Cannot list directory contents" >&2

# Verify files are actually on disk
if [ -f "$CHALLENGE_DIR/1337crypt_output.txt" ]; then
    FILE_SIZE=$(stat -f%z "$CHALLENGE_DIR/1337crypt_output.txt" 2>/dev/null || stat -c%s "$CHALLENGE_DIR/1337crypt_output.txt" 2>/dev/null || echo "unknown")
    echo "[+] 1337crypt_output.txt exists, size: $FILE_SIZE bytes"
else
    echo "[!] ERROR: 1337crypt_output.txt missing after sync!" >&2
fi

if [ -f "$CHALLENGE_DIR/README.txt" ]; then
    FILE_SIZE=$(stat -f%z "$CHALLENGE_DIR/README.txt" 2>/dev/null || stat -c%s "$CHALLENGE_DIR/README.txt" 2>/dev/null || echo "unknown")
    echo "[+] README.txt exists, size: $FILE_SIZE bytes"
else
    echo "[!] ERROR: README.txt missing after sync!" >&2
fi

echo "[+] Challenge setup complete!"

