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
### 1) Find the signal TLS/443 flow
1. Open `net-02-doh-rhythm.pcap` in Wireshark.
2. Apply a broad filter:
   - `tcp.port == 443`
3. Click through a few flows and look for the one where the client→server payload repeatedly starts with TLS record bytes:
   - `17 03 03` (Application Data, TLS 1.2 record layer)
4. Once you’ve identified that 4‑tuple (client IP:port → server IP:443), lock it in with a filter like:
   - `ip.addr == <client_ip> && ip.addr == <server_ip> && tcp.port == 443`

### 2) Make Wireshark decode the record layer (Wireshark 4.x)
Because there is no full TLS handshake, Wireshark may not automatically apply the TLS dissector.
1. Right‑click one of the packets in the signal flow → **Decode As…**
2. Select **Transport: TCP** and set **Current** (or both directions) to **TLS**
3. Apply.

Now you should be able to add the TLS length field as a column:
- Expand **TLS** → **TLS Record Layer** → and right‑click **Length** → **Apply as Column**
  - Field name in recent Wireshark builds is typically: `tls.record.length`

### 3) Extract the lengths you need
1. Keep only **client → server** packets (the direction that carries the channel).
2. Export the displayed packet list:
   - **File → Export Packet Dissections → As CSV…**
3. Ensure your CSV contains:
   - `tls.record.length` (or the Length column you added)

### 4) Decode (KEY + FLAG)
For each extracted TLS record length \(L\):
1. Keep only values that fit the encoding:
   - \(L = 480 + 7v\) where \(v \in [0, 31]\)
2. Convert \(v\) to a Base32 symbol using:
   - `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`
3. Base32‑decode the resulting string to plaintext.

You should see:
- `KEY: ...`
- `FLAG: TDHCTF{...}`

## Author verifier
You can validate locally using:
- `python3 challenges/net-02-doh-rhythm/src/verify_decode.py`


