#!/usr/bin/env python3
"""
Author-side verifier for NET-01.

Decodes challenge-files/net-01-onion-pcap/net-01-onion-pcap.pcap and prints recovered flag.
Pure python, no deps.
"""

from __future__ import annotations

import base64
import os
import struct
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Pkt:
    ts_us: int
    data: bytes


def read_pcap_pkts(pcap_path: str) -> list[Pkt]:
    with open(pcap_path, "rb") as f:
        gh = f.read(24)
        if len(gh) != 24:
            raise ValueError("bad pcap")
        pkts: list[Pkt] = []
        while True:
            ph = f.read(16)
            if not ph:
                break
            if len(ph) != 16:
                raise ValueError("truncated packet header")
            ts_sec, ts_usec, incl, _orig = struct.unpack("<IIII", ph)
            data = f.read(incl)
            if len(data) != incl:
                raise ValueError("truncated packet data")
            pkts.append(Pkt(ts_us=(ts_sec * 1_000_000 + ts_usec), data=data))
        return pkts


def parse_dns_query_name(dns_data: bytes, offset: int) -> tuple[str, int]:
    """Parse DNS QNAME from DNS packet data, starting at offset"""
    labels = []
    pos = offset
    jumped = False
    max_jumps = 10
    jump_count = 0
    
    while pos < len(dns_data):
        if jump_count > max_jumps:
            break
        length = dns_data[pos]
        if length == 0:
            pos += 1
            break
        # DNS compression pointer
        if (length & 0xC0) == 0xC0:
            if pos + 1 >= len(dns_data):
                break
            ptr = ((length & 0x3F) << 8) | dns_data[pos + 1]
            if not jumped:
                pos += 2
            pos = ptr
            jumped = True
            jump_count += 1
            continue
        # Regular label
        if length > 63 or pos + 1 + length > len(dns_data):
            break
        label = dns_data[pos + 1:pos + 1 + length].decode("ascii", errors="ignore")
        labels.append(label)
        pos += 1 + length
        if jumped:
            break
    
    return ".".join(labels), pos


def extract_dns_chunks(pkts: list[Pkt]) -> list[str]:
    """Extract Base64 chunks from DNS query names in the signal flow"""
    chunks: list[tuple[int, str]] = []
    signal_client = "10.0.5.42"
    signal_server = "10.0.5.53"
    exfil_marker = ".blueprint.professor.royalmint.local"
    
    for p in pkts:
        fr = p.data
        if len(fr) < 14 + 20 + 8:
            continue
        
        # Ethernet
        ethertype = struct.unpack("!H", fr[12:14])[0]
        if ethertype != 0x0800:
            continue
        
        # IPv4
        ip = fr[14:]
        if len(ip) < 20:
            continue
        ver_ihl = ip[0]
        if (ver_ihl >> 4) != 4:
            continue
        ihl = (ver_ihl & 0x0F) * 4
        if len(ip) < ihl + 8:
            continue
        
        proto = ip[9]
        if proto != 17:  # UDP
            continue
        
        src_ip = ".".join(str(b) for b in ip[12:16])
        dst_ip = ".".join(str(b) for b in ip[16:20])
        
        # Check if this is from the signal client
        if src_ip != signal_client or dst_ip != signal_server:
            continue

        # UDP
        udp = ip[ihl:]
        if len(udp) < 8:
            continue
        sport, dport = struct.unpack("!HH", udp[0:4])
        if dport != 53:  # DNS
            continue

        # DNS
        dns = udp[8:]
        if len(dns) < 12:
            continue
        
        # DNS header: check if it's a query (QR=0)
        flags = struct.unpack("!H", dns[2:4])[0]
        if (flags & 0x8000) != 0:  # Response, not query
            continue

        # Parse QNAME
        try:
            qname, _ = parse_dns_query_name(dns, 12)
            # Check if it matches our exfiltration pattern
            if exfil_marker in qname:
                # Extract the Base64 chunk (first label)
                chunk = qname.split(".")[0]
                # Base64 URL-safe uses A-Z, a-z, 0-9, -, _
                if len(chunk) > 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in chunk):
                    chunks.append((p.ts_us, chunk))
        except:
            pass
    
    # Capture is shuffled; order by timestamp to reconstruct the exfil stream.
    chunks.sort(key=lambda t: t[0])
    return [c for _ts, c in chunks]


def main() -> None:
    if len(sys.argv) > 1:
        pcap_path = os.path.abspath(sys.argv[1])
    else:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    pcap_path = os.path.join(repo_root, "challenge-files", "net-01-onion-pcap", "net-01-onion-pcap.pcap")
    pkts = read_pcap_pkts(pcap_path)
    chunks = extract_dns_chunks(pkts)
    
    # Concatenate and decode Base64 (URL-safe)
    b64_string = "".join(chunks)
    if not b64_string:
        print("ERROR: No DNS chunks found")
        return
    
    # Add padding if needed (Base64 requires length to be multiple of 4)
    pad = "=" * ((4 - (len(b64_string) % 4)) % 4)
    try:
        decoded = base64.urlsafe_b64decode(b64_string + pad).decode("utf-8", errors="replace")
    # Expected format:
    #   KEY:<...>
    #   FLAG:TDHCTF{...}
        print(decoded.strip())
    except Exception as e:
        print(f"ERROR decoding: {e}")
        print(f"Base64 string: {b64_string}")


if __name__ == "__main__":
    main()
