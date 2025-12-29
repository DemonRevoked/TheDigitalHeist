#!/usr/bin/env python3
"""
Author-side verifier for DF-02.

Extracts the embedded fragmented gzip by:
  - locating gzip header (1f 8b 08)
  - removing the injected gap blocks delimited by:
      <<DIRECTORATE_SCRUB_GAP>> ... <</DIRECTORATE_SCRUB_GAP>>
  - then decompressing and printing the recovered blueprint text
"""

from __future__ import annotations

import gzip
import io
import os


GAP_START = b"<<DIRECTORATE_SCRUB_GAP>>\n"
GAP_END = b"\n<</DIRECTORATE_SCRUB_GAP>>"


def remove_gaps(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(data):
        j = data.find(GAP_START, i)
        if j == -1:
            out += data[i:]
            break
        out += data[i:j]
        k = data.find(GAP_END, j + len(GAP_START))
        if k == -1:
            break
        i = k + len(GAP_END)
    return bytes(out)


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    p = os.path.join(repo_root, "challenge-files", "df-02-burned-usb", "burned-usb.img")
    with open(p, "rb") as f:
        blob = f.read()

    # Avoid false positives: only search for gzip header after our known marker.
    marker = b"USBIMGv1\n"
    # Use the last occurrence to avoid extremely unlikely collisions in noisy bytes.
    m = blob.rfind(marker)
    start = 0 if m == -1 else (m + len(marker))

    hdr = blob.find(b"\x1f\x8b\x08", start)
    if hdr == -1:
        raise SystemExit("[!] gzip header not found")

    carved = blob[hdr:]
    cleaned = remove_gaps(carved)
    # Be tolerant of trailing bytes (players/tools may carve beyond exact gzip end).
    with gzip.GzipFile(fileobj=io.BytesIO(cleaned)) as gf:
        plain = gf.read()
    print(plain.decode("utf-8", errors="replace").strip())


if __name__ == "__main__":
    main()


