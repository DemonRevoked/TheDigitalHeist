# crypto-02-vault-breach — Walkthrough

## Goal
Break the RSA in `encrypted_vault.txt` and read the decrypted message (the flag).

## Steps
1. **Open the challenge file**
   - Read `encrypted_vault.txt`.
   - Copy these numbers:
     - `n`
     - `e`
     - `c`

2. **Factor n (Fermat method)**
   - This RSA uses two primes that are very close.
   - Fermat factoring works well when primes are close.

3. **Build the private key**
   - After you find `p` and `q`:
     - `phi = (p-1)*(q-1)`
     - `d = inverse(e, phi)`

4. **Decrypt**
   - `m = pow(c, d, n)`
   - Convert `m` to bytes and read the text.
   - That text is the flag.

