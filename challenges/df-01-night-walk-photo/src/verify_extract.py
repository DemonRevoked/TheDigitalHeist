#!/usr/bin/env python3
"""
Author-side verifier for DF-01.

Parses the JPEG COM segment and prints recovered values.
Pure python, no deps.
"""

from __future__ import annotations

import os
import sys


def extract_com_comments(jpeg: bytes) -> list[bytes]:
    if len(jpeg) < 2 or jpeg[0:2] != b"\xFF\xD8":
        raise ValueError("not a jpeg")
    i = 2
    comments = []
    while i + 4 <= len(jpeg):
        if jpeg[i] != 0xFF:
            # Scan forward (JPEG markers are aligned; this keeps verifier robust for our tiny file)
            i += 1
            continue
        marker = jpeg[i : i + 2]
        i += 2
        if marker == b"\xFF\xDA":  # SOS, image data begins; stop
            break
        if i + 2 > len(jpeg):
            break
        seg_len = int.from_bytes(jpeg[i : i + 2], "big")
        i += 2
        if seg_len < 2 or i + (seg_len - 2) > len(jpeg):
            break
        payload = jpeg[i : i + (seg_len - 2)]
        i += seg_len - 2
        if marker == b"\xFF\xFE":  # COM
            comments.append(payload)
    return comments


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    p = os.path.join(repo_root, "challenge-files", "df-01-night-walk-photo", "night-walk.jpg")
    with open(p, "rb") as f:
        data = f.read()
    comments = extract_com_comments(data)
    if not comments:
        print("[!] No COM comment found")
        return 2
    text = b"\n---\n".join(comments).decode("utf-8", errors="replace")
    print(text.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


