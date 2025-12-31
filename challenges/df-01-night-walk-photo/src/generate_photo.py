#!/usr/bin/env python3
"""
DF-01 generator (pure python, no deps).

Writes:
  challenge-files/df-01-night-walk-photo/night-walk.jpg
  challenge-files/df-01-night-walk-photo/README.txt

The JPEG includes a COM (comment) segment with:
  - Human-readable "field capture" metadata (UNIT/GPS/etc)
  - A binary blob marker containing an encrypted+compressed payload (KEY/FLAG)

Goal: make extraction *non-trivial* (not solvable by naive strings/xxd),
while still being solvable with DF tooling + a bit of decoding.
"""

from __future__ import annotations

import base64
import textwrap
import gzip
import io
import os
from datetime import datetime, timezone


FLAG = "TDHCTF{exif_shadow_unit}"
UNIT_CODE = "SHADOW-17"
CAMERA_MODEL = "Kestrel-X3"
GPS_STR = "51.5033N,0.1195W"

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

    raise RuntimeError("Missing challenge key: set CHALLENGE_KEY or generate keys/*.key via startup.sh")


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

    # Human-readable part (still discoverable via metadata tools).
    # IMPORTANT: do not reveal the exact decode chain here; this is player-facing.
    header_text = (
        "DIRECTORATE FIELD CAPTURE // NIGHT WALK\n"
        f"CapturedUTC:{now}\n"
        f"CameraModel:{CAMERA_MODEL}\n"
        "DateTimeOriginal:2024:06:19 22:41:03\n"
        f"GPS:{GPS_STR}\n"
        f"UNIT:{UNIT_CODE}\n"
        "Note: Directorate sanitizer detected. Payload moved to a packed blob.\n"
        "Note2: The blob is NOT human-readable as-is.\n"
    ).encode("utf-8")

    # Hidden payload (NOT plaintext in the JPEG anymore)
    payload = f"KEY:{key}\nFLAG:{FLAG}\n".encode("utf-8")
    # Use gzip so decoding can be done with standard tools:
    #   base64 -d | gunzip -c
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(payload)
    packed = buf.getvalue()

    # Medium difficulty: keep it non-plaintext (so strings/xxd won't trivially reveal),
    # but make decoding straightforward: base64-decode + zlib-decompress.
    b64 = base64.b64encode(packed).decode("ascii")
    b64_wrapped = "\n".join(textwrap.wrap(b64, width=76)).encode("utf-8")

    comment = (
        header_text
        + b"--BEGIN-BLOB-B64--\n"
        + b64_wrapped
        + b"\n--END-BLOB-B64--\n"
    )

    template = base64.b64decode(_TINY_JPEG_B64)
    out_jpeg = _inject_com_segment(template, comment)

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
            "- Recover BOTH values hidden in the photo metadata/comment blob:\n"
            "  - KEY:<challenge key>\n"
            "  - FLAG:TDHCTF{exif_shadow_unit}\n\n"
            "Hints (in-story):\n"
            "- The Directorate doesn’t just delete evidence — it repackages it.\n"
            "- Start where investigators start: metadata, comments, and “harmless” fields.\n"
            "- If you find a long wrapped blob, treat it like a standard transport wrapper.\n"
            "- Contradictory timestamps are intentional misdirection; focus on what repeats.\n"
        )


if __name__ == "__main__":
    main()


