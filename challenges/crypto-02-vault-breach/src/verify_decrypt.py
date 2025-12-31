#!/usr/bin/env python3
"""
Author-side verifier / player helper for CRYPTO-02 (no deps).

Given encrypted_vault.txt, performs:
- Fermat factorization (works because p and q are intentionally close)
- RSA private exponent recovery
- Decrypt ciphertext and print plaintext

Usage:
  python3 verify_decrypt.py [path/to/encrypted_vault.txt]
"""

from __future__ import annotations

import math
import os
import re
import sys


def parse_params(text: str) -> tuple[int, int, int]:
    n_m = re.search(r"^\s*n\s*=\s*(\d+)\s*$", text, re.M)
    e_m = re.search(r"^\s*e\s*=\s*(\d+)\s*$", text, re.M)
    c_m = re.search(r"^\s*c\s*=\s*(\d+)\s*$", text, re.M)
    if not (n_m and e_m and c_m):
        raise SystemExit("[!] Could not parse n/e/c from file")
    return int(n_m.group(1)), int(e_m.group(1)), int(c_m.group(1))


def fermat_factor(n: int) -> tuple[int, int]:
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    while True:
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            p = a - b
            q = a + b
            return p, q
        a += 1


def main() -> None:
    if len(sys.argv) > 1:
        path = os.path.abspath(sys.argv[1])
    else:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        path = os.path.join(repo_root, "challenge-files", "crypto-02-vault-breach", "encrypted_vault.txt")

    text = open(path, "r", encoding="utf-8", errors="ignore").read()
    n, e, c = parse_params(text)

    p, q = fermat_factor(n)
    if p * q != n:
        raise SystemExit("[!] Factorization failed (p*q != n)")

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    pt = m.to_bytes((m.bit_length() + 7) // 8, "big").decode("utf-8", errors="replace").strip()
    print(pt)


if __name__ == "__main__":
    main()


