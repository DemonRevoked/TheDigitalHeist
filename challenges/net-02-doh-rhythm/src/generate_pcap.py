#!/usr/bin/env python3
"""
NET-02 generator (pure python, no deps).

Real-world HTTP header exfiltration technique:
- Data is encoded in HTTP request headers (User-Agent, Referer, etc.)
- Base64 or hex encoding to make it header-safe
- Multiple HTTP requests carry the exfiltrated data
- Decoy HTTP traffic mixed in to make detection harder

This technique is used by real malware and APT groups to exfiltrate data
through HTTP requests that look like normal web traffic.

Output:
  challenge-files/net-02-doh-rhythm/net-02-doh-rhythm.pcap
  challenge-files/net-02-doh-rhythm/README.txt
"""

from __future__ import annotations

import base64
import os
import random
import struct
import time
from dataclasses import dataclass
from ipaddress import IPv4Address


def _u16(x: int) -> int:
    return x & 0xFFFF


def _u32(x: int) -> int:
    return x & 0xFFFFFFFF


def checksum16(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    s = 0
    for i in range(0, len(data), 2):
        s += (data[i] << 8) + data[i + 1]
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


def ipv4_bytes(ip: str) -> bytes:
    return int(IPv4Address(ip)).to_bytes(4, "big")


def build_ipv4(payload: bytes, src: str, dst: str, proto: int, ident: int, ttl: int = 64) -> bytes:
    ver_ihl = (4 << 4) | 5
    tos = 0
    total_len = 20 + len(payload)
    flags_frag = 0
    hdr = struct.pack(
        "!BBHHHBBH4s4s",
        ver_ihl,
        tos,
        total_len,
        _u16(ident),
        flags_frag,
        ttl,
        proto,
        0,
        ipv4_bytes(src),
        ipv4_bytes(dst),
    )
    csum = checksum16(hdr)
    hdr = hdr[:10] + struct.pack("!H", csum) + hdr[12:]
    return hdr + payload


def tcp_checksum_ipv4(src: str, dst: str, tcp_seg: bytes) -> int:
    pseudo = ipv4_bytes(src) + ipv4_bytes(dst) + struct.pack("!BBH", 0, 6, len(tcp_seg))
    return checksum16(pseudo + tcp_seg)


def build_tcp(
    payload: bytes,
    src_ip: str,
    dst_ip: str,
    sport: int,
    dport: int,
    seq: int,
    ack: int,
    flags: int,
    window: int,
) -> bytes:
    data_offset = 5
    off_flags = (data_offset << 12) | (flags & 0x01FF)
    hdr = struct.pack("!HHIIHHHH", sport, dport, _u32(seq), _u32(ack), off_flags, _u16(window), 0, 0)
    seg = hdr + payload
    csum = tcp_checksum_ipv4(src_ip, dst_ip, seg)
    hdr = hdr[:16] + struct.pack("!H", csum) + hdr[18:]
    return hdr + payload


PCAP_GLOBAL = struct.pack(
    "<IHHIIII",
    0xA1B2C3D4,
    2,
    4,
    0,
    0,
    65535,
    1,  # LINKTYPE_ETHERNET
)


def pcap_pkt(ts_sec: int, ts_usec: int, frame: bytes) -> bytes:
    incl = len(frame)
    return struct.pack("<IIII", ts_sec, ts_usec, incl, incl) + frame


def mac_bytes(mac: str) -> bytes:
    return bytes(int(b, 16) for b in mac.split(":"))


def build_ether(payload: bytes, src: str, dst: str, ethertype: int) -> bytes:
    return mac_bytes(dst) + mac_bytes(src) + struct.pack("!H", ethertype) + payload


@dataclass
class Frame:
    ts_us: int
    data: bytes


def build_http_request(method: str, path: str, host: str, user_agent: str = "", referer: str = "", custom_header: str = "") -> bytes:
    """
    Build a simple HTTP/1.1 request.
    Real-world exfiltration often uses User-Agent or custom headers.
    """
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    if user_agent:
        request += f"User-Agent: {user_agent}\r\n"
    if referer:
        request += f"Referer: {referer}\r\n"
    if custom_header:
        request += f"{custom_header}\r\n"
    request += "Accept: */*\r\n"
    request += "Connection: keep-alive\r\n"
    request += "\r\n"
    return request.encode("utf-8")


def main() -> None:
    random.seed(424242)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    out_dir = os.path.join(repo_root, "challenge-files", "net-02-doh-rhythm")
    os.makedirs(out_dir, exist_ok=True)

    # Flag matches Tasks.md placeholder.
    flag = "TDHCTF{dns_tunnel_key}"

    # Per-deployment challenge key
    challenge_key = os.environ.get("CHALLENGE_KEY", "").strip()
    if not challenge_key:
        for cand in ("net-02-doh-rhythm.key", "net-02.key"):
            p = os.path.join(repo_root, "keys", cand)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    challenge_key = fh.read().strip()
                break
    if not challenge_key:
        raise RuntimeError("Missing challenge key: set CHALLENGE_KEY or generate keys/*.key via startup.sh")

    message = f"KEY:{challenge_key}\nFLAG:{flag}\n".encode("utf-8")

    # Encode message in Base64 (URL-safe, commonly used in HTTP header exfiltration)
    # Real-world: attackers use Base64 because it's header-safe and compact
    b64 = base64.urlsafe_b64encode(message).decode("ascii").rstrip("=")

    # Real-world HTTP header exfiltration: split Base64 into chunks
    # Common technique: encode data in User-Agent or custom headers
    # Each HTTP request carries a chunk in a header value
    CHUNK_SIZE = 20  # 20 Base64 chars per HTTP request (reasonable header length)
    chunks = [b64[i:i+CHUNK_SIZE] for i in range(0, len(b64), CHUNK_SIZE)]

    # Real flow (the "signal")
    c_ip = "10.13.37.10"
    s_ip = "10.13.37.80"  # HTTP server
    c_port = 51022
    s_port = 80

    # Decoy flows (noise)
    decoys: list[tuple[str, str, int, int]] = []
    for i in range(11, 31):  # 20 decoy clients
        decoys.append((f"10.13.37.{i}", "10.13.37.80", 51000 + i, 80))

    mac_src = "02:42:ac:11:00:10"
    mac_dst = "02:42:ac:11:00:11"

    frames: list[Frame] = []
    t0 = int(time.time())
    now_us = t0 * 1_000_000

    # Background noise: legitimate-looking HTTP traffic
    def emit_background_noise(count: int) -> None:
        nonlocal now_us
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]
        paths = ["/", "/index.html", "/api/status", "/health", "/favicon.ico", "/static/style.css"]
        for _ in range(count):
            src_ip = f"10.13.{random.randrange(0, 50)}.{random.randrange(2, 254)}"
            dst_ip = f"10.13.{random.randrange(0, 50)}.{random.randrange(2, 254)}"
            sport = random.randrange(1024, 65535)
            dport = random.choice([80, 8080, 443])
            
            # Random HTTP request
            path = random.choice(paths)
            host = f"server{random.randrange(1, 10)}.internal.corp"
            ua = random.choice(user_agents)
            http_req = build_http_request("GET", path, host, user_agent=ua)
            
            # Not a fully realistic TCP exchange; good enough for offline background noise.
            tcp = build_tcp(http_req, src_ip, dst_ip, sport, dport, random.randrange(0, 2**32), 0, 0x18, 64240)
            ip = build_ipv4(tcp, src_ip, dst_ip, proto=6, ident=random.randrange(0, 65536), ttl=random.choice([52, 64, 127]))
            frames.append(Frame(now_us + random.randrange(0, 2_400_000), build_ether(ip, mac_src, mac_dst, 0x0800)))

    emit_background_noise(4500)

    def emit_http_flow(src_ip: str, dst_ip: str, sport: int, dport: int, requests: list[bytes]):
        nonlocal now_us
        seq_c = 1000 + random.randrange(0, 5000)
        seq_s = 7000 + random.randrange(0, 5000)

        # 3-way handshake
        syn = build_tcp(b"", src_ip, dst_ip, sport, dport, seq_c, 0, flags=0x02, window=64240)
        ip = build_ipv4(syn, src_ip, dst_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
        frames.append(Frame(now_us, build_ether(ip, mac_src, mac_dst, 0x0800)))
        now_us += 5_000

        synack = build_tcp(b"", dst_ip, src_ip, dport, sport, seq_s, seq_c + 1, flags=0x12, window=64240)
        ip = build_ipv4(synack, dst_ip, src_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
        frames.append(Frame(now_us, build_ether(ip, mac_dst, mac_src, 0x0800)))
        now_us += 5_000

        ack = build_tcp(b"", src_ip, dst_ip, sport, dport, seq_c + 1, seq_s + 1, flags=0x10, window=64240)
        ip = build_ipv4(ack, src_ip, dst_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
        frames.append(Frame(now_us, build_ether(ip, mac_src, mac_dst, 0x0800)))
        now_us += 10_000

        seq_c += 1
        seq_s += 1

        # HTTP requests
        for req in requests:
            now_us += random.randrange(50_000, 200_000)  # Realistic timing between requests
            seg = build_tcp(req, src_ip, dst_ip, sport, dport, seq_c, seq_s, flags=0x18, window=64240)
            seq_c = (seq_c + len(req)) & 0xFFFFFFFF
            ip = build_ipv4(seg, src_ip, dst_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
            frames.append(Frame(now_us, build_ether(ip, mac_src, mac_dst, 0x0800)))
            
            # Server response (ACK)
            now_us += 5_000
            resp_payload = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
            resp_seg = build_tcp(resp_payload, dst_ip, src_ip, dport, sport, seq_s, seq_c, flags=0x18, window=64240)
            seq_s = (seq_s + len(resp_payload)) & 0xFFFFFFFF
            ip = build_ipv4(resp_seg, dst_ip, src_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
            frames.append(Frame(now_us, build_ether(ip, mac_dst, mac_src, 0x0800)))

    # Build signal HTTP requests: encode Base64 chunks in User-Agent header
    # Real-world: User-Agent is commonly used because it's expected to vary
    signal_requests: list[bytes] = []
    base_host = "metrics.internal.corp"
    
    for i, chunk in enumerate(chunks):
        # Encode chunk in User-Agent header
        # Format: "Mozilla/5.0 (compatible; ExfilChunk-<chunk>)"
        user_agent = f"Mozilla/5.0 (compatible; ExfilChunk-{chunk})"
        path = f"/api/metrics?id={random.randrange(1000, 9999)}"  # Looks like normal API calls
        http_req = build_http_request("GET", path, base_host, user_agent=user_agent)
        signal_requests.append(http_req)

    # Add some prelude/tail requests to make it look more normal
    for _ in range(5):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        path = f"/api/health?t={random.randrange(1000000, 9999999)}"
        signal_requests.insert(0, build_http_request("GET", path, base_host, user_agent=ua))
    for _ in range(5):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        path = f"/api/status?t={random.randrange(1000000, 9999999)}"
        signal_requests.append(build_http_request("GET", path, base_host, user_agent=ua))

    emit_http_flow(c_ip, s_ip, c_port, s_port, signal_requests)

    # Decoy flows: similar HTTP requests but without the exfiltration pattern
    for dip, sip, dp, sp in decoys:
        decoy_requests: list[bytes] = []
        for _ in range(random.randint(10, 30)):
            ua = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            ])
            path = f"/api/data?id={random.randrange(1000, 9999)}"
            host = f"server{random.randrange(1, 5)}.internal.corp"
            decoy_requests.append(build_http_request("GET", path, host, user_agent=ua))
        emit_http_flow(dip, sip, dp, sp, decoy_requests)

    # Sort by timestamp
    frames.sort(key=lambda fr: fr.ts_us)
    # Add micro-jitter
    jittered: list[Frame] = []
    for fr in frames:
        jittered.append(Frame(fr.ts_us + random.randrange(0, 2_000), fr.data))

    out_pcap = os.path.join(out_dir, "net-02-doh-rhythm.pcap")
    with open(out_pcap, "wb") as f:
        f.write(PCAP_GLOBAL)
        for fr in jittered:
            ts_sec = fr.ts_us // 1_000_000
            ts_usec = fr.ts_us % 1_000_000
            f.write(pcap_pkt(int(ts_sec), int(ts_usec), fr.data))

    out_readme = os.path.join(out_dir, "README.txt")
    with open(out_readme, "w", encoding="utf-8") as f:
        f.write(
            "=== NET-02: DoH Rhythm — HTTP Header Exfiltration ===\n\n"
            "You captured internal HTTP traffic. A rogue agent is exfiltrating data\n"
            "using HTTP header exfiltration—a real-world technique used by malware\n"
            "and APT groups to bypass DLP and network monitoring.\n\n"
            "Files:\n"
            "- net-02-doh-rhythm.pcap\n\n"
            "Objective:\n"
            "- Recover BOTH values hidden in the capture:\n"
            "  - KEY: <challenge key>\n"
            "  - FLAG: TDHCTF{...}\n\n"
            "Notes:\n"
            "- The data is encoded in HTTP request headers.\n"
            "- Look for HTTP requests from a specific client IP.\n"
            "- The encoding uses Base64 (common in real HTTP exfiltration).\n"
            "- Not all HTTP requests contain the signal—filter carefully.\n"
        )

    print(f"[+] Wrote {out_pcap}")
    print(f"[+] Wrote {out_readme}")


if __name__ == "__main__":
    main()
