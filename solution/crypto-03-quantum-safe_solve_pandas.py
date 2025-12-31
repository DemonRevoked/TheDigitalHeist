#!/usr/bin/env python3
"""
CRYPTO-03 solver (pandas-based parser).

Reads 1337crypt_output.txt using pandas, extracts:
  hint, D, n, c
Then factors n using the hint and decrypts Goldwasser–Micali bits.

Usage:
  python3 crypto-03-quantum-safe_solve_pandas.py /path/to/1337crypt_output.txt

Notes:
- Requires pandas: pip install pandas
- Pure-Python math/decimal; no Sage required.
"""

from __future__ import annotations

import ast
import math
import sys
from decimal import Decimal, getcontext, ROUND_HALF_EVEN


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 crypto-03-quantum-safe_solve_pandas.py 1337crypt_output.txt")

    path = sys.argv[1]

    try:
        import pandas as pd  # type: ignore
    except Exception:
        raise SystemExit("pandas not installed. Install with: pip install pandas")

    # File format is line-based: `key = value`
    # Example:
    #   hint = 123
    #   D = 456
    #   n = 789
    #   c = [ ... ]
    df = pd.read_csv(
        path,
        sep=r"\s*=\s*",
        engine="python",
        header=None,
        names=["k", "v"],
        dtype=str,
        keep_default_na=False,
    )

    def get_one(name: str) -> str:
        s = df.loc[df["k"].str.strip() == name, "v"]
        if s.empty:
            raise SystemExit(f"Missing '{name}' in file")
        return str(s.iloc[0]).strip()

    hint = int(get_one("hint"))
    D = int(get_one("D"))
    n = int(get_one("n"))
    c_str = get_one("c")
    c = ast.literal_eval(c_str)

    # High precision is needed for the sqrt-based rounding step.
    getcontext().prec = 20000
    s = Decimal(hint) / Decimal(D)
    sqrt_n = Decimal(n).sqrt()

    # Recover p+q using the identity:
    # (sqrt(p)+sqrt(q))^2 = p+q + 2*sqrt(n)
    S = int((s * s - Decimal(2) * sqrt_n).to_integral_value(rounding=ROUND_HALF_EVEN))

    disc = S * S - 4 * n
    root = math.isqrt(disc)
    if root * root != disc:
        raise SystemExit(
            "Failed to factor n (discriminant not a perfect square). "
            "This usually means you're solving an older artifact; regenerate crypto-03 so D is very large."
        )

    p = (S - root) // 2
    q = (S + root) // 2
    if p * q != n:
        raise SystemExit("Factorization check failed (p*q != n).")

    def legendre(a: int, p_: int) -> int:
        r = pow(a % p_, (p_ - 1) // 2, p_)
        return -1 if r == p_ - 1 else 1

    # bit=0 -> legendre(ci,p) = -1
    # bit=1 -> legendre(ci,p) = +1
    bits = [(1 if legendre(ci, p) == 1 else 0) for ci in c]

    m = 0
    for b in bits:
        m = (m << 1) | b

    pt = m.to_bytes((m.bit_length() + 7) // 8, "big").decode("utf-8", errors="replace").strip()
    print(pt)


if __name__ == "__main__":
    main()


