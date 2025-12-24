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
