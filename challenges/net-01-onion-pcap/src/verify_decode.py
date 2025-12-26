#!/usr/bin/env python3
"""
Author-side verifier for NET-01.

Decodes challenge-files/net-01/capture.pcap and prints recovered flag.
Pure python, no deps.
"""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass


def _u16(x: int) -> int:
    return x & 0xFFFF


def read_pcap_frames(pcap_path: str) -> list[bytes]:
    with open(pcap_path, "rb") as f:
        gh = f.read(24)
        if len(gh) != 24:
            raise ValueError("bad pcap")
        frames = []
        while True:
            ph = f.read(16)
            if not ph:
                break
            if len(ph) != 16:
                raise ValueError("truncated packet header")
            _ts_sec, _ts_usec, incl, _orig = struct.unpack("<IIII", ph)
            data = f.read(incl)
            if len(data) != incl:
                raise ValueError("truncated packet data")
            frames.append(data)
        return frames


@dataclass
class Record:
    idx: int
    ip_id_low: int
    ts_low: int


def parse_net01_records(frames: list[bytes]) -> list[Record]:
    records: list[Record] = []
    for fr in frames:
        if len(fr) < 14 + 4:
            continue
        # Ether + VLAN
        ethertype = struct.unpack("!H", fr[12:14])[0]
        if ethertype != 0x8100:
            continue
        tci = struct.unpack("!H", fr[14:16])[0]
        vlan = tci & 0x0FFF
        if vlan != 133:
            continue
        inner_ethertype = struct.unpack("!H", fr[16:18])[0]
        if inner_ethertype != 0x0800:
            continue
        ip = fr[18:]
        if len(ip) < 20:
            continue
        ver_ihl = ip[0]
        if (ver_ihl >> 4) != 4:
            continue
        ihl = (ver_ihl & 0x0F) * 4
        if len(ip) < ihl + 4:
            continue
        proto = ip[9]
        if proto != 47:  # GRE
            continue
        src4 = ".".join(str(b) for b in ip[12:16])
        dst4 = ".".join(str(b) for b in ip[16:20])
        if not (src4 == "198.51.100.10" and dst4 == "203.0.113.20"):
            continue
        ip_id = struct.unpack("!H", ip[4:6])[0]
        ip_id_low = ip_id & 0xFF

        gre = ip[ihl:]
        if len(gre) < 4:
            continue
        gre_proto = struct.unpack("!H", gre[2:4])[0]
        if gre_proto != 0x86DD:
            continue

        ip6 = gre[4:]
        if len(ip6) < 40:
            continue
        if (ip6[0] >> 4) != 6:
            continue
        src6 = ip6[8:24]
        dst6 = ip6[24:40]
        if not (
            src6 == bytes.fromhex("20010db8133700000000000000000010")
            and dst6 == bytes.fromhex("20010db8133700000000000000000020")
        ):
            continue
        flow_label = ((ip6[1] & 0x0F) << 16) | (ip6[2] << 8) | ip6[3]
        idx = flow_label & 0xFFF
        next_header = ip6[6]
        if next_header != 6:
            continue
        tcp = ip6[40:]
        if len(tcp) < 20:
            continue
        sport, dport = struct.unpack("!HH", tcp[0:4])
        if not (sport == 41414 and dport == 443):
            continue
        data_offset = (tcp[12] >> 4) * 4
        if len(tcp) < data_offset:
            continue
        opts = tcp[20:data_offset]
        # Find TS option (kind=8,len=10) preceded by NOPs in our generator
        ts_low = None
        i = 0
        while i < len(opts):
            kind = opts[i]
            if kind == 0:
                break
            if kind == 1:
                i += 1
                continue
            if i + 1 >= len(opts):
                break
            ln = opts[i + 1]
            if ln < 2 or i + ln > len(opts):
                break
            if kind == 8 and ln == 10 and i + 10 <= len(opts):
                tsval = struct.unpack("!I", opts[i + 2 : i + 6])[0]
                ts_low = tsval & 0xFF
                break
            i += ln
        if ts_low is None:
            continue

        records.append(Record(idx=idx, ip_id_low=ip_id_low, ts_low=ts_low))
    return records


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    pcap_path = os.path.join(repo_root, "challenge-files", "net-01-onion-pcap", "net-01-onion-pcap.pcap")
    frames = read_pcap_frames(pcap_path)
    recs = parse_net01_records(frames)
    recs.sort(key=lambda r: r.idx)

    # Reconstruct ciphertext byte: c = ip_id_low ^ ts_low
    cbytes = bytes((_u16(r.ip_id_low) ^ _u16(r.ts_low)) & 0xFF for r in recs)

    # Decrypt: b = c ^ key ^ idx
    # key = (sport ^ dport) & 0xFF = (41414 ^ 443) & 0xFF
    key = (41414 ^ 443) & 0xFF
    plain = bytes((c ^ key ^ (i & 0xFF)) & 0xFF for i, c in enumerate(cbytes))
    # Expected format:
    #   KEY:<...>
    #   FLAG:TDHCTF{...}
    print(plain.decode("utf-8", errors="replace").strip())


if __name__ == "__main__":
    main()


