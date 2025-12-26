# crypto-03-quantum-safe — Walkthrough

## Goal
Decrypt `1337crypt_output.txt` to recover:
- `KEY: ...`
- `FLAG: ...`

## Steps
1. **Open the output**
   - Read `1337crypt_output.txt`.
   - Copy:
     - `hint`
     - `D`
     - `n`
     - `c` (the list)

2. **Recover p and q from the hint**
   - Compute:
     - `s = hint / D`
   - `s` is basically:
     - `s = sqrt(p) + sqrt(q)`
   - Then:
     - `s^2 = p + q + 2*sqrt(n)`
     - So `p + q = s^2 - 2*sqrt(n)`
   - Now solve the normal RSA equations:
     - `p*q = n`
     - `p + q = known_value`

3. **Decrypt each bit**
   - For each number in `c`:
     - If `legendre_symbol(ci, p) == 1` then bit = 0
     - If `legendre_symbol(ci, p) == -1` then bit = 1

4. **Turn bits into text**
   - Join bits → number → bytes → string.
   - You will see:
     - `KEY: ...`
     - `FLAG: ...`

