#!/usr/bin/env python3
"""
NET-01 generator (pure python, no deps).

Real-world DNS tunneling exfiltration technique:
- Data is encoded in DNS query names (subdomain labels)
- Base64 URL-safe encoding (DNS-compatible) to make it DNS-safe
- Multiple DNS queries carry the exfiltrated data
- Decoy DNS queries mixed in to make detection harder

This technique is used by real malware like Iodine, dnscat2, and DNSStager.

Output:
  challenge-files/net-01-onion-pcap/net-01-onion-pcap.pcap
  challenge-files/net-01-onion-pcap/README.txt
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


def mac_bytes(mac: str) -> bytes:
    return bytes(int(b, 16) for b in mac.split(":"))


def ipv4_bytes(ip: str) -> bytes:
    return int(IPv4Address(ip)).to_bytes(4, "big")


def build_ether(payload: bytes, src: str, dst: str, ethertype: int) -> bytes:
    return mac_bytes(dst) + mac_bytes(src) + struct.pack("!H", ethertype) + payload


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


def build_udp(payload: bytes, sport: int, dport: int) -> bytes:
    length = 8 + len(payload)
    return struct.pack("!HHHH", sport, dport, length, 0) + payload


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


def build_http_request(method: str, path: str, host: str, user_agent: str) -> bytes:
    req = f"{method} {path} HTTP/1.1\r\n"
    req += f"Host: {host}\r\n"
    req += f"User-Agent: {user_agent}\r\n"
    req += "Accept: */*\r\n"
    req += "Connection: keep-alive\r\n"
    req += "\r\n"
    return req.encode("utf-8")


def dns_encode_label(label: str) -> bytes:
    """Encode a DNS label (max 63 chars)"""
    label_bytes = label.encode("ascii")
    if len(label_bytes) > 63:
        raise ValueError("DNS label too long")
    return bytes([len(label_bytes)]) + label_bytes


def build_dns_query(qname: str, qtype: int = 1, qclass: int = 1) -> bytes:
    """
    Build a DNS query packet.
    qname: Domain name (e.g., "data.example.com")
    qtype: Query type (1 = A record)
    qclass: Query class (1 = IN)
    """
    # DNS header
    transaction_id = random.randrange(1, 65536)
    flags = 0x0100  # Standard query, recursion desired
    questions = 1
    answer_rrs = 0
    authority_rrs = 0
    additional_rrs = 0
    
    header = struct.pack("!HHHHHH", transaction_id, flags, questions, answer_rrs, authority_rrs, additional_rrs)
    
    # Encode QNAME (domain name)
    qname_bytes = b""
    for part in qname.split("."):
        if part:
            qname_bytes += dns_encode_label(part)
    qname_bytes += b"\x00"  # Null terminator
    
    # QTYPE and QCLASS
    question = struct.pack("!HH", qtype, qclass)
    
    return header + qname_bytes + question


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
    orig = len(frame)
    return struct.pack("<IIII", ts_sec, ts_usec, incl, orig) + frame


@dataclass
class Frame:
    ts_us: int
    data: bytes


def main() -> None:
    random.seed(1337)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    out_dir = os.path.join(repo_root, "challenge-files", "net-01-onion-pcap")
    os.makedirs(out_dir, exist_ok=True)

    # Flag matches Tasks.md placeholder
    flag = "TDHCTF{rogue_engineer_signal}"

    # Per-deployment challenge key
    challenge_key = os.environ.get("CHALLENGE_KEY", "").strip()
    if not challenge_key:
        for cand in ("net-01-onion-pcap.key", "net-01.key"):
            p = os.path.join(repo_root, "keys", cand)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    challenge_key = fh.read().strip()
                break
    if not challenge_key:
        raise RuntimeError("Missing challenge key: set CHALLENGE_KEY or generate keys/*.key via startup.sh")

    message = f"KEY:{challenge_key}\nFLAG:{flag}\n".encode("utf-8")

    # Encode message in Base64 (URL-safe for DNS compatibility)
    # URL-safe Base64 uses - and _ instead of + and /, making it DNS-safe
    b64 = base64.urlsafe_b64encode(message).decode("ascii").rstrip("=")

    # Real-world DNS tunneling: split Base64 into chunks and encode in subdomain labels
    # Common technique: each chunk becomes a subdomain label
    # Example: "S0VZOmFiY2Q" -> "s0vzomfiyy2q.data.example.com"
    CHUNK_SIZE = 10  # 10 Base64 chars per DNS label (Base64 is more efficient than Base32)
    chunks = [b64[i:i+CHUNK_SIZE] for i in range(0, len(b64), CHUNK_SIZE)]
    
    # Storyline-hint domain (players can filter by this).
    # Keep it "realistic enough" (corp-ish) but themed to the heist storyline.
    base_domain = "professor.royalmint.local"
    exfil_suffix = "blueprint"
    
    # Network setup
    client_ip = "10.0.5.42"
    dns_server_ip = "10.0.5.53"
    client_port = 54321
    dns_port = 53

    # Add some HTTP traffic for realism (client does normal web beacons too).
    http_server_ip = "10.0.5.80"
    http_host = "cctv.royalmint.local"
    http_sport = 49152
    http_dport = 80
    
    mac_src = "02:42:ac:11:00:02"
    mac_dst = "02:42:ac:11:00:01"

    frames: list[Frame] = []
    t0 = int(time.time())
    now_us = t0 * 1_000_000

    # Add background noise (legitimate-looking DNS queries)
    NOISE_DNS_QUERIES = 2000
    DECOY_EXFIL_QUERIES = 500

    def add_noise_dns(count: int) -> None:
        nonlocal frames, now_us
        legitimate_domains = [
            "www.royalmint.local",
            "auth.royalmint.local",
            "cdn.royalmint.local",
            "cctv.royalmint.local",
            "vault.royalmint.local",
            "ops.professor.royalmint.local",
            "telemetry.professor.royalmint.local",
            "updates.tokyo.crew.local",
            "chat.nairobi.crew.local",
        ]
        for _ in range(count):
            domain = random.choice(legitimate_domains)
            if random.random() < 0.3:
                # Add random subdomain
                subdomain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(3, 8)))
                domain = f"{subdomain}.{domain}"
            
            dns_query = build_dns_query(domain)
            udp = build_udp(dns_query, random.randrange(1024, 65535), dns_port)
            src_ip = f"10.0.{random.randrange(0, 10)}.{random.randrange(1, 254)}"
            dst_ip = f"10.0.{random.randrange(0, 10)}.{random.randrange(1, 254)}"
            ip = build_ipv4(udp, src_ip, dst_ip, proto=17, ident=random.randrange(0, 65536), ttl=random.choice([52, 64, 127]))
            frame = build_ether(ip, mac_src, mac_dst, 0x0800)
            frames.append(Frame(ts_us=now_us + random.randrange(0, 3_000_000), data=frame))

    def add_decoy_exfil(count: int) -> None:
        """Add decoy exfiltration queries that look similar but don't decode correctly"""
        nonlocal frames, now_us
        for _ in range(count):
            # Generate random Base64-like chunks
            fake_chunk = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_', k=random.randint(5, 12)))
            # Decoy uses a *different* suffix so solvers can lock onto the storyline hint suffix.
            fake_domain = f"{fake_chunk.lower()}.draft.{base_domain}"
            dns_query = build_dns_query(fake_domain)
            udp = build_udp(dns_query, random.randrange(1024, 65535), dns_port)
            # Use different source IPs to make it harder
            src_ip = f"10.0.{random.randrange(0, 10)}.{random.randrange(1, 254)}"
            ip = build_ipv4(udp, src_ip, dns_server_ip, proto=17, ident=random.randrange(0, 65536), ttl=64)
            frame = build_ether(ip, mac_src, mac_dst, 0x0800)
            frames.append(Frame(ts_us=now_us + random.randrange(0, 3_000_000), data=frame))

    # Add noise first
    add_noise_dns(NOISE_DNS_QUERIES)
    add_decoy_exfil(DECOY_EXFIL_QUERIES)

    def emit_http_keepalive(request_times: list[int]) -> None:
        """
        Emit a single keep-alive HTTP flow from client_ip -> http_server_ip.
        We send one request shortly after each DNS exfil query timestamp.
        """
        nonlocal frames
        if not request_times:
            return

        # Sequence numbers
        seq_c = 1000 + random.randrange(0, 5000)
        seq_s = 7000 + random.randrange(0, 5000)

        # Handshake shortly before the first scheduled request
        t_handshake = max(0, request_times[0] - 25_000)

        syn = build_tcp(b"", client_ip, http_server_ip, http_sport, http_dport, seq_c, 0, flags=0x02, window=64240)
        ip = build_ipv4(syn, client_ip, http_server_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
        frames.append(Frame(ts_us=t_handshake, data=build_ether(ip, mac_src, mac_dst, 0x0800)))

        synack = build_tcp(b"", http_server_ip, client_ip, http_dport, http_sport, seq_s, seq_c + 1, flags=0x12, window=64240)
        ip = build_ipv4(synack, http_server_ip, client_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
        frames.append(Frame(ts_us=t_handshake + 5_000, data=build_ether(ip, mac_dst, mac_src, 0x0800)))

        ack = build_tcp(b"", client_ip, http_server_ip, http_sport, http_dport, seq_c + 1, seq_s + 1, flags=0x10, window=64240)
        ip = build_ipv4(ack, client_ip, http_server_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
        frames.append(Frame(ts_us=t_handshake + 10_000, data=build_ether(ip, mac_src, mac_dst, 0x0800)))

        seq_c += 1
        seq_s += 1

        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        for k, t_req in enumerate(request_times):
            # Request after DNS query
            path = f"/pixel.gif?cam=hall&seq={k}&t={t_req}"
            req = build_http_request("GET", path, http_host, user_agent=ua)
            seg = build_tcp(req, client_ip, http_server_ip, http_sport, http_dport, seq_c, seq_s, flags=0x18, window=64240)
            ip = build_ipv4(seg, client_ip, http_server_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
            frames.append(Frame(ts_us=t_req, data=build_ether(ip, mac_src, mac_dst, 0x0800)))
            seq_c = (seq_c + len(req)) & 0xFFFFFFFF

            # Tiny server response
            resp = b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n"
            seg = build_tcp(resp, http_server_ip, client_ip, http_dport, http_sport, seq_s, seq_c, flags=0x18, window=64240)
            ip = build_ipv4(seg, http_server_ip, client_ip, proto=6, ident=random.randrange(0, 65536), ttl=64)
            frames.append(Frame(ts_us=t_req + 5_000, data=build_ether(ip, mac_dst, mac_src, 0x0800)))
            seq_s = (seq_s + len(resp)) & 0xFFFFFFFF

    # Real exfiltration: encode data in DNS query names
    http_request_times: list[int] = []
    for i, chunk in enumerate(chunks):
        # Build domain: <chunk>.<exfil_suffix>.<base_domain>
        # IMPORTANT: Base64 is case-sensitive, so we MUST preserve case in the label.
        exfil_domain = f"{chunk}.{exfil_suffix}.{base_domain}"
        
        dns_query = build_dns_query(exfil_domain)
        udp = build_udp(dns_query, client_port, dns_port)
        ip = build_ipv4(udp, client_ip, dns_server_ip, proto=17, ident=1000 + i, ttl=64)
        frame = build_ether(ip, mac_src, mac_dst, 0x0800)

        # Space out queries (realistic timing: 100-500ms between queries)
        ts_us = (t0 * 1_000_000) + (i * 200_000) + random.randrange(0, 100_000)
        frames.append(Frame(ts_us=ts_us, data=frame))

        # After every DNS query, emit a small HTTP beacon a moment later (realistic multi-protocol host).
        http_request_times.append(ts_us + random.randrange(25_000, 60_000))

    emit_http_keepalive(sorted(http_request_times))

    # Add a decoy flow with fake flag in a different pattern
    fake_flag = "TDHCTF{this_is_a_decoy_flag_do_not_submit}"
    fake_b64 = base64.urlsafe_b64encode(fake_flag.encode()).decode("ascii").rstrip("=")
    fake_chunks = [fake_b64[i:i+CHUNK_SIZE] for i in range(0, len(fake_b64), CHUNK_SIZE)]
    decoy_client = "10.0.5.99"
    for j, chunk in enumerate(fake_chunks[:8]):  # Only first 8 chunks
        # Keep case here too (so the decoy is decodable if someone follows it).
        exfil_domain = f"{chunk}.backup.{base_domain}"
        dns_query = build_dns_query(exfil_domain)
        udp = build_udp(dns_query, 54322, dns_port)
        ip = build_ipv4(udp, decoy_client, dns_server_ip, proto=17, ident=5000 + j, ttl=64)
        frame = build_ether(ip, mac_src, mac_dst, 0x0800)
        ts_us = (t0 * 1_000_000) + 1_000_000 + (j * 150_000)
        frames.append(Frame(ts_us=ts_us, data=frame))

    # Shuffle to make it harder (but players can filter by client IP)
    random.shuffle(frames)

    # Write PCAP
    out_pcap = os.path.join(out_dir, "net-01-onion-pcap.pcap")
    with open(out_pcap, "wb") as f:
        f.write(PCAP_GLOBAL)
        for fr in frames:
            ts_sec = fr.ts_us // 1_000_000
            ts_usec = fr.ts_us % 1_000_000
            f.write(pcap_pkt(int(ts_sec), int(ts_usec), fr.data))

    # Write player-facing README
    out_readme = os.path.join(out_dir, "README.txt")
    with open(out_readme, "w", encoding="utf-8") as f:
        f.write(
            "=== NET-01: Onion PCAP — DNS Tunneling Exfiltration ===\n\n"
            "You recovered a network capture from the Royal Mint internal network.\n"
            "A rogue engineer is exfiltrating data using DNS tunneling—a real-world\n"
            "technique used by malware and attackers to bypass network restrictions.\n\n"
            "Files:\n"
            "- net-01-onion-pcap.pcap\n\n"
            "Objective:\n"
            "- Recover BOTH values hidden in the capture:\n"
            "  - KEY: <challenge key>\n"
            "  - FLAG: TDHCTF{...}\n\n"
            "Notes:\n"
            "- The data is encoded in DNS query names (subdomain labels).\n"
            "- Look for DNS queries matching a themed domain hint.\n"
            "- The encoding uses Base64 URL-safe encoding (DNS-compatible).\n"
            "- The same host also generates normal HTTP beacon traffic.\n"
            "- Not all DNS queries contain the signal—filter carefully.\n"
        )

    print(f"[+] Wrote {out_pcap}")
    print(f"[+] Wrote {out_readme}")


if __name__ == '__main__':
    main()
