## crypto-02-vault-breach — Walkthrough (RSA close primes → Fermat)

### Goal
Decrypt `encrypted_vault.txt` to recover **both** values from the decrypted plaintext:
- `KEY:<challenge key>`
- `FLAG:TDHCTF{vault_breach_decrypted}`

### Key insight
This RSA instance is weak because **p and q are very close**, making it vulnerable to **Fermat factorization**:
\[
n = p \cdot q,\quad p \approx q
\]

### Python solve (pure stdlib)
If your file formatting differs (Windows line endings, extra spaces, etc.), the safest approach is to **copy/paste the numbers** for `n`, `e`, and `c` and let the solver prompt you.

```bash
python3 - << 'PY'
import math

print("Paste the RSA parameters from encrypted_vault.txt (digits only).")
n = int(input("n = ").strip())
e = int(input("e = ").strip())
c = int(input("c = ").strip())

# Fermat: find a,b such that n = a^2 - b^2 = (a-b)(a+b)
a = math.isqrt(n)
if a * a < n:
    a += 1
while True:
    b2 = a * a - n
    b = math.isqrt(b2)
    if b * b == b2:
        p = a - b
        q = a + b
        break
    a += 1

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)
pt = m.to_bytes((m.bit_length() + 7) // 8, "big").decode("utf-8", errors="replace").strip()
print(pt)
PY
```

### What you should see
- New builds (after the generator fix) will decrypt to:
  - `KEY:<...>`
  - `FLAG:TDHCTF{vault_breach_decrypted}`

- If you’re solving an **older artifact**, it may decrypt to a single key-derived flag like:
  - `TDHCTF{78b04447...}`
  That means you have the **old file**. Download/regenerate the updated `encrypted_vault.txt` and re-run the same solver.

