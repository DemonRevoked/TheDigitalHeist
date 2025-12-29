#!/usr/bin/env python3
"""
DF-01 generator (pure python, no deps).

Writes:
  challenge-files/df-01-night-walk-photo/night-walk.jpg
  challenge-files/df-01-night-walk-photo/README.txt

The JPEG includes a COM (comment) segment containing:
  KEY:<per-start key>
  FLAG:TDHCTF{exif_shadow_unit}
  UNIT:<unit code>

This is intentionally "forensics-medium": EXIF/metadata extraction is the intended path.
"""

from __future__ import annotations

import base64
import os
from datetime import datetime, timezone


FLAG = "TDHCTF{exif_shadow_unit}"
UNIT_CODE = "SHADOW-17"

# 1x1 pixel valid JPEG (tiny). We inject a COM segment after SOI.
_TINY_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
    "AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
    "AQH/wAALCAAaABoBAREA/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAA"
    "AAAAAAAAAAAB/9oADAMBAAIQAxAAAAFf/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQAB"
    "PwA//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAgEBPwA//8QAFBEBAAAAAAAAAAAAAAAAA"
    "AAAAP/aAAgBAwEBPwA//9k="
)


def _read_key(repo_root: str) -> str:
    # Priority: env CHALLENGE_KEY > keys/df-01-night-walk-photo.key > keys/df-01.key > fallback.
    k = os.environ.get("CHALLENGE_KEY", "").strip()
    if k:
        return k

    for cand in ("df-01-night-walk-photo.key", "df-01.key"):
        p = os.path.join(repo_root, "keys", cand)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                return fh.read().strip()

    return "offline-session-key"


def _inject_com_segment(jpeg: bytes, comment: bytes) -> bytes:
    # JPEG structure: starts with SOI 0xFFD8. Insert COM marker 0xFFFE right after SOI.
    if len(jpeg) < 2 or jpeg[0:2] != b"\xFF\xD8":
        raise ValueError("template is not a JPEG (missing SOI)")

    # COM segment: marker (2) + length (2, includes length field) + payload
    if len(comment) > 0xFF00:
        raise ValueError("comment too large")
    seg_len = len(comment) + 2
    com = b"\xFF\xFE" + seg_len.to_bytes(2, "big") + comment
    return jpeg[0:2] + com + jpeg[2:]


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    out_dir = os.path.join(repo_root, "challenge-files", "df-01-night-walk-photo")
    os.makedirs(out_dir, exist_ok=True)

    key = _read_key(repo_root)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # "Manipulated EXIF" vibe: include contradictory-looking metadata lines in the comment.
    # Player will still recover UNIT + KEY + FLAG from metadata extraction tools.
    comment_text = (
        "DIRECTORATE FIELD CAPTURE // NIGHT WALK\n"
        f"CapturedUTC:{now}\n"
        "CameraModel:Kestrel-X3\n"
        "DateTimeOriginal:2024:06:19 22:41:03\n"
        "GPS:51.5033N,0.1195W\n"
        f"UNIT:{UNIT_CODE}\n"
        f"KEY:{key}\n"
        f"FLAG:{FLAG}\n"
    )

    template = base64.b64decode(_TINY_JPEG_B64)
    out_jpeg = _inject_com_segment(template, comment_text.encode("utf-8"))

    with open(os.path.join(out_dir, "night-walk.jpg"), "wb") as f:
        f.write(out_jpeg)

    with open(os.path.join(out_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "=== DF-01: The Night Walk Photo ===\n\n"
            "Narrative:\n"
            "A Directorate field agent posted a photo. The Directorate tried to 'sanitize' it,\n"
            "but operational metadata still leaks through.\n\n"
            "Files:\n"
            "- night-walk.jpg\n\n"
            "Objective:\n"
            "- Recover BOTH values from the file's metadata:\n"
            "  - KEY:<challenge key>\n"
            "  - FLAG:TDHCTF{exif_shadow_unit}\n\n"
            "Tips:\n"
            "- Start with metadata tools (EXIF/XMP/comments).\n"
            "- If your tool shows multiple contradictory timestamps, that's intentional.\n"
        )


if __name__ == "__main__":
    main()


