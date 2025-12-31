## crypto-03-quantum-safe — Walkthrough (Goldwasser–Micali + factor leak)

### Goal
Decrypt `1337crypt_output.txt` to recover:
- `KEY: <challenge key>`
- `FLAG: TDHCTF{quantum_safe_decrypted}`

### Key insight
This is **Goldwasser–Micali (GM)** bit-by-bit encryption. To decrypt GM you must **factor \(n\)** into \(p,q\).

The challenge leaks a “sqrt-sum” style hint:
- `hint = floor(D*(sqrt(p) + sqrt(q)))`
- `D` is intentionally **very large** (so rounding becomes stable)

Once you recover \(p\) and \(q\), each ciphertext element reveals one bit via the **Legendre symbol**.

### Python solve (pure stdlib)
Run from repo root:

```bash
cd /home/demon/TheDigitalHeist/challenge-files/crypto-03-quantum-safe
python3 - << 'PY'
import ast, re, math
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

text = open("1337crypt_output.txt", "r", encoding="utf-8", errors="ignore").read()
hint = int(re.search(r"^hint\\s*=\\s*(\\d+)", text, re.M).group(1))
D = int(re.search(r"^D\\s*=\\s*(\\d+)", text, re.M).group(1))
n = int(re.search(r"^n\\s*=\\s*(\\d+)", text, re.M).group(1))
c = ast.literal_eval(re.search(r"^c\\s*=\\s*(\\[.*\\])\\s*$", text, re.M | re.S).group(1))

# High precision is needed for the sqrt-based rounding step.
getcontext().prec = 20000
s = Decimal(hint) / Decimal(D)
sqrt_n = Decimal(n).sqrt()

# Recover p+q using the identity:
# (sqrt(p)+sqrt(q))^2 = p+q + 2*sqrt(n)
S = int((s*s - Decimal(2)*sqrt_n).to_integral_value(rounding=ROUND_HALF_EVEN))

disc = S*S - 4*n
root = math.isqrt(disc)
if root*root != disc:
    raise SystemExit("Failed to factor n (rounding too noisy).")

p = (S - root) // 2
q = (S + root) // 2
if p*q != n:
    raise SystemExit("Factorization check failed.")

def legendre(a: int, p: int) -> int:
    # returns +1 or -1 for a != 0 mod p
    r = pow(a % p, (p - 1) // 2, p)
    return -1 if r == p - 1 else 1

# In the generator, x is chosen so that legendre(x,p) = legendre(x,q) = -1.
# Cipher construction uses x^(odd + bit) * r^(even), so:
#   bit=0 -> legendre(ci,p) = -1
#   bit=1 -> legendre(ci,p) = +1
bits = [(1 if legendre(ci, p) == 1 else 0) for ci in c]

m = 0
for b in bits:
    m = (m << 1) | b

pt = m.to_bytes((m.bit_length() + 7) // 8, "big").decode("utf-8", errors="replace").strip()
print(pt)
PY
```

### Python solve (paste full file contents — no file I/O)
If you're solving on another machine (or you don’t want any parsing/file path issues), you can **paste the entire `1337crypt_output.txt`** into stdin.

#### Option A (recommended): interactive paste (type `END` when done)
Run this, paste the entire file, then type `END` on its own line and press Enter:

```bash
python3 - << 'PY'
import ast, re, math, sys
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

print("Paste the full contents of 1337crypt_output.txt now.", file=sys.stderr)
print("When finished, type END on a new line and press Enter.", file=sys.stderr)

lines = []
while True:
    try:
        line = input()
    except EOFError:
        # allow Ctrl-D/Ctrl-Z too, but END is clearer
        break
    if line.strip() == "END":
        break
    lines.append(line)

blob = "\n".join(lines) + "\n"

hint_m = re.search(r"^hint\\s*=\\s*(\\d+)\\s*$", blob, re.M)
D_m = re.search(r"^D\\s*=\\s*(\\d+)\\s*$", blob, re.M)
n_m = re.search(r"^n\\s*=\\s*(\\d+)\\s*$", blob, re.M)
c_m = re.search(r"^c\\s*=\\s*(\\[.*\\])\\s*$", blob, re.M | re.S)
if not (hint_m and D_m and n_m and c_m):
    raise SystemExit("Could not find hint/D/n/c in pasted text. Paste the entire file verbatim.")

hint = int(hint_m.group(1))
D = int(D_m.group(1))
n = int(n_m.group(1))
c = ast.literal_eval(c_m.group(1))

# High precision is needed for the sqrt-based rounding step.
getcontext().prec = 20000
s = Decimal(hint) / Decimal(D)
sqrt_n = Decimal(n).sqrt()

# Recover p+q using the identity:
# (sqrt(p)+sqrt(q))^2 = p+q + 2*sqrt(n)
S = int((s*s - Decimal(2)*sqrt_n).to_integral_value(rounding=ROUND_HALF_EVEN))

disc = S*S - 4*n
root = math.isqrt(disc)
if root*root != disc:
    raise SystemExit(
        "Failed to factor n (rounding too noisy). "
        "This usually means you're solving an older artifact; regenerate crypto-03 so D is very large."
    )

p = (S - root) // 2
q = (S + root) // 2
if p*q != n:
    raise SystemExit("Factorization check failed.")

def legendre(a: int, p: int) -> int:
    r = pow(a % p, (p - 1) // 2, p)
    return -1 if r == p - 1 else 1

# bit=0 -> legendre(ci,p) = -1
# bit=1 -> legendre(ci,p) = +1
bits = [(1 if legendre(ci, p) == 1 else 0) for ci in c]

m = 0
for b in bits:
    m = (m << 1) | b

pt = m.to_bytes((m.bit_length() + 7) // 8, "big").decode("utf-8", errors="replace").strip()
print(pt)
PY
```

#### Option B: classic stdin paste (Ctrl‑D/Ctrl‑Z)
If you prefer EOF style input:
- Linux/macOS: end paste with **Ctrl‑D**
- Windows: end paste with **Ctrl‑Z**, then Enter

### Expected output
You should see:
- `KEY: ...`
- `FLAG: TDHCTF{quantum_safe_decrypted}`

