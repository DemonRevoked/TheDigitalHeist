#!/usr/bin/env python3
"""
DF-02 generator (pure python, no deps).

Writes:
  challenge-files/df-02-burned-usb/burned-usb.img
  challenge-files/df-02-burned-usb/README.txt

The "disk image" is a raw blob containing a deliberately fragmented gzip stream.
When the gzip stream is reconstructed (remove gap blocks), it reveals:
  KEY:<per-start key>
  FLAG:TDHCTF{carved_network_node}
  NODE:<node label>
"""

from __future__ import annotations

import gzip
import os
import random


FLAG = "TDHCTF{carved_network_node}"
NODE = "SAFEHOUSE-REGISTRY"


def _read_key(repo_root: str) -> str:
    # Priority: env CHALLENGE_KEY > keys/df-02-burned-usb.key > keys/df-02.key > fallback.
    k = os.environ.get("CHALLENGE_KEY", "").strip()
    if k:
        return k

    for cand in ("df-02-burned-usb.key", "df-02.key"):
        p = os.path.join(repo_root, "keys", cand)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                return fh.read().strip()

    raise RuntimeError("Missing challenge key: set CHALLENGE_KEY or generate keys/*.key via startup.sh")


def main() -> None:
    random.seed(2025)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    out_dir = os.path.join(repo_root, "challenge-files", "df-02-burned-usb")
    os.makedirs(out_dir, exist_ok=True)

    key = _read_key(repo_root)

    blueprint = (
        "=== DIRECTORATE CORE BLUEPRINT (RECOVERED) ===\n"
        "\n"
        "           [GATEWAY]----[DoH Relay]----[Δ₀ Ingest]\n"
        "                 \\                      |\n"
        "                  \\----[Safehouse]----[Evidence Hash Registry]\n"
        "\n"
        "Critical pivot node (label):\n"
        f"NODE:{NODE}\n"
        "\n"
        "Deployment authentication (do not share):\n"
        f"KEY:{key}\n"
        f"FLAG:{FLAG}\n"
    ).encode("utf-8")

    gz = gzip.compress(blueprint, compresslevel=9)

    # Fragment the gzip stream into 3 parts and inject noisy "gap blocks" between them.
    a = len(gz) // 3
    b = (2 * len(gz)) // 3
    p1, p2, p3 = gz[:a], gz[a:b], gz[b:]

    gap_marker_start = b"<<DIRECTORATE_SCRUB_GAP>>\n"
    gap_marker_end = b"\n<</DIRECTORATE_SCRUB_GAP>>"

    def gap_block(sz: int) -> bytes:
        # Gap block contains printable noise + random bytes to simulate corruption/rewrites.
        text = (
            b"TIMESTAMP_REWRITE=ENABLED\n"
            b"LOG_CLEANUP_UNIT=ACTIVE\n"
            b"NOTE:payload_irrecoverable\n"
        )
        noise = os.urandom(max(0, sz - len(text)))
        return gap_marker_start + text + noise + gap_marker_end

    blob = bytearray()
    # Use deterministic filler to avoid accidental marker/header collisions in the verifier
    # while still looking like a "raw image" to players.
    blob += (b"\x00" * 4096)
    # Decoy flag string (trap for strings-based solvers)
    blob += b"\nTDHCTF{this_is_a_decoy_flag_do_not_submit}\n"
    blob += os.urandom(2048)
    blob += b"USBIMGv1\n"
    blob += p1
    blob += gap_block(1800)
    blob += p2
    blob += gap_block(2600)
    blob += p3
    # IMPORTANT: keep gzip stream at end-of-file so simple carving-to-EOF produces a valid .gz.

    with open(os.path.join(out_dir, "burned-usb.img"), "wb") as f:
        f.write(bytes(blob))

    with open(os.path.join(out_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "=== DF-02: Burned USB ===\n\n"
            "Narrative:\n"
            "A half-destroyed USB stick was pulled from a Directorate cleanup burn bag.\n"
            "Your job: carve and reconstruct what they tried to erase.\n\n"
            "Files:\n"
            "- burned-usb.img\n\n"
            "Objective:\n"
            "- Recover BOTH values hidden in the image:\n"
            "  - KEY:<challenge key>\n"
            "  - FLAG:TDHCTF{carved_network_node}\n\n"
            "Hints (in-story):\n"
            "- The cleanup unit didn’t wipe the drive clean — it interrupted the truth.\n"
            "- Look for a “core document” that still has structure, then work outward.\n"
            "- Expect deliberate gaps and noise inserted to break simple carving.\n"
            "- The most obvious flag-shaped string is not the real one.\n"
        )


if __name__ == "__main__":
    main()


