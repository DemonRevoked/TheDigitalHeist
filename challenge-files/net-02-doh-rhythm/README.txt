=== NET-02: DoH Rhythm — Metadata Exfil ===

You captured internal traffic to a 'DoH gateway'. Everything is encrypted.
The Directorate still leaked the key via metadata.

Files:
- net-02-doh-rhythm.pcap

Objective:
- Recover BOTH values hidden in the capture:
  - KEY: <challenge key>
  - FLAG: TDHCTF{...}

Notes:
- Decryption is not required and not possible from this capture.
- Focus on metadata: sizes, timing, patterns.
