# net-02-doh-rhythm — Walkthrough (DoH Rhythm / Metadata Exfil)

## Goal
Recover **both** values from `challenge-files/net-02-doh-rhythm/net-02-doh-rhythm.pcap`:
- `KEY: <challenge key>`
- `FLAG: TDHCTF{...}`

## Key insight
You **cannot** (and do not need to) decrypt anything. The flag leaks through **metadata**:
- pick the correct TCP/443 flow (one of several decoys)
- read the TLS-like **record lengths**
- map lengths → Base32 alphabet → decode to text

## Solve outline
1. Identify the “signal” flow:
   - look for a client→server burst of many TLS Application Data records (`0x17 0x03 0x03`)
   - record lengths follow a tight arithmetic progression (not random)
2. Extract every client→server TLS record length \(L\).
3. Keep only values where:
   - \(L = 480 + 7v\) for some integer \(v\) in \([0,31]\)
4. Convert each \(v\) to Base32 symbol using:
   - `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`
5. Base32-decode the resulting string; you should see:
   - `KEY: ...`
   - `FLAG: ...`

## Author verifier
You can validate locally using:
- `python3 challenges/net-02-doh-rhythm/src/verify_decode.py`


