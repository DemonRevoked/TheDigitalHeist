#!/usr/bin/env python3
"""
Author-side verifier for NET-02.

Decodes HTTP header exfiltration from challenge-files/net-02-doh-rhythm/net-02-doh-rhythm.pcap and prints recovered flag.
Pure python, no deps.
"""

from __future__ import annotations

import base64
import os
import re
import struct
import sys
from dataclasses import dataclass


PCAP_GH_LEN = 24
PCAP_PH_LEN = 16


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
    # Ether + IPv4 + TCP
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


def extract_http_user_agent(payload: bytes) -> str | None:
    """Extract User-Agent header from HTTP request"""
    try:
        text = payload.decode("utf-8", errors="ignore")
        # Look for User-Agent header
        match = re.search(r'User-Agent:\s*([^\r\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except:
        pass
    return None


def main() -> None:
    if len(sys.argv) > 1:
        pcap_path = os.path.abspath(sys.argv[1])
    else:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        pcap_path = os.path.join(repo_root, "challenge-files", "net-02-doh-rhythm", "net-02-doh-rhythm.pcap")
    pkts = read_pcap(pcap_path)

    # Signal flow tuple
    c_ip, s_ip, c_port, s_port = "10.13.37.10", "10.13.37.80", 51022, 80

    # Extract Base64 chunks from User-Agent headers
    chunks: list[str] = []
    for p in pkts:
        parsed = parse_ipv4_tcp(p.data)
        if not parsed:
            continue
        src, dst, sport, dport, flags, payload = parsed
        # Only client->server packets (PSH+ACK or just data)
        if not (src == c_ip and dst == s_ip and sport == c_port and dport == s_port):
            continue
        if len(payload) < 10:  # Minimum HTTP request size
            continue
        
        # Extract User-Agent header
        ua = extract_http_user_agent(payload)
        if not ua:
            continue
        
        # Look for ExfilChunk pattern
        match = re.search(r'ExfilChunk-([A-Za-z0-9_-]+)', ua)
        if match:
            chunk = match.group(1)
            chunks.append(chunk)

    # Concatenate and decode Base64
    b64_string = "".join(chunks)
    if not b64_string:
        print("ERROR: No HTTP header chunks found")
        return
    
    # Add padding if needed (Base64 requires length to be multiple of 4)
    pad = "=" * ((4 - (len(b64_string) % 4)) % 4)
    try:
        decoded = base64.urlsafe_b64decode(b64_string + pad).decode("utf-8", errors="ignore")
        # Expected format:
        #   KEY:<...>
        #   FLAG:TDHCTF{...}
        decoded = decoded.strip()
        if "KEY:" in decoded and "FLAG:" in decoded:
            print(decoded)
            return
        # Fallback: try to find flag
        m = re.search(r"TDHCTF\{[^}]+\}", decoded)
        print(decoded if decoded else (m.group(0) if m else ""))
    except Exception as e:
        print(f"ERROR decoding: {e}")
        print(f"Base64 string: {b64_string}")


if __name__ == "__main__":
    main()
