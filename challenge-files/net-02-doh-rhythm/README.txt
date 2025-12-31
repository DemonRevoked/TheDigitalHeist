=== NET-02: DoH Rhythm — HTTP Header Exfiltration ===

You captured internal HTTP traffic. A rogue agent is exfiltrating data
using HTTP header exfiltration—a real-world technique used by malware
and APT groups to bypass DLP and network monitoring.

Files:
- net-02-doh-rhythm.pcap

Objective:
- Recover BOTH values hidden in the capture:
  - KEY: <challenge key>
  - FLAG: TDHCTF{...}

Notes:
- The data is encoded in HTTP request headers.
- Look for HTTP requests from a specific client IP.
- The encoding uses Base64 (common in real HTTP exfiltration).
- Not all HTTP requests contain the signal—filter carefully.
