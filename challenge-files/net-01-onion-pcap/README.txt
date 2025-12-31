=== NET-01: Onion PCAP — DNS Tunneling Exfiltration ===

You recovered a network capture from the Royal Mint internal network.
A rogue engineer is exfiltrating data using DNS tunneling—a real-world
technique used by malware and attackers to bypass network restrictions.

Files:
- net-01-onion-pcap.pcap

Objective:
- Recover BOTH values hidden in the capture:
  - KEY: <challenge key>
  - FLAG: TDHCTF{...}

Notes:
- The data is encoded in DNS query names (subdomain labels).
- Look for DNS queries matching a themed domain hint.
- The encoding uses Base64 URL-safe encoding (DNS-compatible).
- The same host also generates normal HTTP beacon traffic.
- Not all DNS queries contain the signal—filter carefully.
