#!/usr/bin/env python3
"""
Author-side verifier for NET-02.

Decodes the metadata side-channel from challenge-files/net-02/capture.pcap and prints recovered flag.
Pure python, no deps.
"""

from __future__ import annotations

import base64
import os
import re
import struct
from dataclasses import dataclass


PCAP_GH_LEN = 24
PCAP_PH_LEN = 16

BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


@dataclass
class Pkt:
    ts_us: int
    data: bytes


def read_pcap(pcap_path: str) -> list[Pkt]:
    with open(pcap_path, "rb") as f:
        gh = f.read(PCAP_GH_LEN)
        if len(gh) != PCAP_GH_LEN:
            raise ValueError("bad pcap")
        pkts: list[Pkt] = []
        while True:
            ph = f.read(PCAP_PH_LEN)
            if not ph:
                break
            if len(ph) != PCAP_PH_LEN:
                raise ValueError("truncated packet header")
            ts_sec, ts_usec, incl, _orig = struct.unpack("<IIII", ph)
            data = f.read(incl)
            if len(data) != incl:
                raise ValueError("truncated packet data")
            pkts.append(Pkt(ts_us=(ts_sec * 1_000_000 + ts_usec), data=data))
        return pkts


def parse_ipv4_tcp(pkt: bytes):
    # Ether + IPv4 + TCP (no VLAN in net-02 generator)
    if len(pkt) < 14 + 20:
        return None
    ethertype = struct.unpack("!H", pkt[12:14])[0]
    if ethertype != 0x0800:
        return None
    ip = pkt[14:]
    if (ip[0] >> 4) != 4:
        return None
    ihl = (ip[0] & 0x0F) * 4
    if len(ip) < ihl + 20:
        return None
    proto = ip[9]
    if proto != 6:
        return None
    src = ".".join(str(b) for b in ip[12:16])
    dst = ".".join(str(b) for b in ip[16:20])
    tcp = ip[ihl:]
    sport, dport = struct.unpack("!HH", tcp[0:4])
    doff = (tcp[12] >> 4) * 4
    if len(tcp) < doff:
        return None
    payload = tcp[doff:]
    flags = tcp[13]
    return src, dst, sport, dport, flags, payload


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    pcap_path = os.path.join(repo_root, "challenge-files", "net-02-doh-rhythm", "net-02-doh-rhythm.pcap")
    pkts = read_pcap(pcap_path)

    # Signal flow tuple
    c_ip, s_ip, c_port, s_port = "10.13.37.10", "10.13.37.53", 51022, 443

    # Extract client->server TLS appdata records and their record lengths
    recs: list[tuple[int, int]] = []  # (ts_us, record_len)
    for p in pkts:
        parsed = parse_ipv4_tcp(p.data)
        if not parsed:
            continue
        src, dst, sport, dport, _flags, payload = parsed
        if not (src == c_ip and dst == s_ip and sport == c_port and dport == s_port):
            continue
        # TLS record header is 5 bytes
        if len(payload) < 5:
            continue
        content_type = payload[0]
        if content_type != 0x17:
            continue
        rec_len = struct.unpack("!H", payload[3:5])[0]
        recs.append((p.ts_us, rec_len))

    # Convert lengths to Base32 symbols: rlen = 480 + v*7
    # Filter only valid ones in that series.
    symbols: list[str] = []
    for _ts, rlen in recs:
        if rlen < 480 or (rlen - 480) % 7 != 0:
            continue
        v = (rlen - 480) // 7
        if 0 <= v < 32:
            symbols.append(BASE32_ALPHABET[v])

    # In the signal flow, non-matching "noise" records use lengths that do not fit the 480+v*7 series,
    # so once we filter by that series we can decode the full stream directly.
    s = "".join(symbols)
    pad = "=" * ((8 - (len(s) % 8)) % 8)
    decoded = base64.b32decode(s + pad).decode("utf-8", errors="ignore")
    # Expected format:
    #   KEY:<...>
    #   FLAG:TDHCTF{...}
    decoded = decoded.strip()
    # If something weird happens, fall back to printing at least the flag token.
    if "KEY:" in decoded and "FLAG:" in decoded:
        print(decoded)
        return
    m = re.search(r"TDHCTF\{[^}]+\}", decoded)
    print(decoded if decoded else (m.group(0) if m else ""))


if __name__ == "__main__":
    main()


