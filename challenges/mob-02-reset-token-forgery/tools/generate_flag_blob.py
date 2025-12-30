#!/usr/bin/env python3
"""
Generate an AES-GCM encrypted blob for embedding in the Android app.

The app derives the AES key as:
  key = SHA-256(secret_utf8)[:16]   # AES-128

Blob encoding:
  base64( nonce_12_bytes || ciphertext_and_tag )
"""

import argparse
import base64
import hashlib
import os
import sys

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception:
    print("Missing dependency: cryptography", file=sys.stderr)
    print("Install: python3 -m pip install cryptography", file=sys.stderr)
    raise


def derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return digest[:16]


def encrypt_flag(secret: str, flag: str) -> str:
    key = derive_key(secret)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    # No associated data (AAD) for simplicity.
    ciphertext_and_tag = aesgcm.encrypt(nonce, flag.encode("utf-8"), None)
    blob = nonce + ciphertext_and_tag
    return base64.b64encode(blob).decode("ascii")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secret", required=True, help="JWT secret string (exact bytes used by app)")
    ap.add_argument("--flag", required=True, help="Flag string, e.g. TDHCTF{...}")
    args = ap.parse_args()

    print(encrypt_flag(args.secret, args.flag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


