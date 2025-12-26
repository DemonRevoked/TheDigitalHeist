# net-01-onion-pcap — Walkthrough (Onion PCAP / Header Whispers)

## Goal
Recover **both** values from `challenge-files/net-01-onion-pcap/net-01-onion-pcap.pcap`:
- `KEY: <challenge key>`
- `FLAG: TDHCTF{...}`

## What’s going on (high level)
The “real” data is **not in payload** (the capture also contains lots of noise/decoys to slow analysis):
- Packets are VLAN tagged
- Outer IPv4 carries **GRE**
- GRE contains inner IPv6/TCP
- Each flag byte is split across:
  - outer IPv4 **Identification** low byte
  - inner TCP **Timestamp (TSval)** low byte
- Packets are **shuffled**; the correct index is stored in IPv6 **flow label** low 12 bits

## Solve outline
### 1) Open and isolate the real tunnel in Wireshark
1. Open `net-01-onion-pcap.pcap` in Wireshark.
2. Apply a first-pass filter to cut the noise:
   - `vlan && ip.proto == 47`
3. Click a packet and expand layers:
   - `Ethernet II`
   - `802.1Q Virtual LAN`
   - `Internet Protocol Version 4`
   - `Generic Routing Encapsulation (GRE)`
   - `Internet Protocol Version 6`
   - `Transmission Control Protocol`
4. Confirm you’re looking at the **signal** flow (not decoys) by checking the *inner* tuple is consistent across many packets:
   - Inner IPv6 src/dst stays the same
   - Inner TCP src port/dst port stays the same

### 2) Add columns for the fields you need
Add these as columns (right-click field → **Apply as Column**):
- **IPv6 flow label**: `ipv6.flow`
- **IPv4 identification**: `ip.id`
- **TCP TSval**: expand `TCP > Options > Timestamps` and add `tcp.options.timestamp.tsval`
- **TCP srcport / dstport**: `tcp.srcport`, `tcp.dstport` (only needed once to compute the 1-byte key)

### 3) Sort into message order
The packets are intentionally shuffled. The ordering index is:
- `idx = (ipv6.flow) & 0x0fff`

In Wireshark:
1. Click the **IPv6 flow label** column header to sort.
2. If you want to be extra safe, add a display filter that keeps only the one inner stream you identified (right-click the inner IPv6 src/dst and ports → “Apply as Filter”).

### 4) Export the packet list as CSV
1. Go to **File → Export Packet Dissections → As CSV…**
2. Export the **Displayed** packets (not “All packets”).
3. Ensure your CSV contains the columns you added: flow label, ip.id, tsval, srcport, dstport.

### 5) Reconstruct the message (KEY + FLAG)
For each packet in sorted order, compute:
- `c = (ip.id & 0xff) XOR (tsval & 0xff)`
- `key = (tcp.srcport XOR tcp.dstport) & 0xff`
- `plain[i] = c XOR key XOR i`

Example reconstruction script (feed it your exported CSV):

```python
import csv
import re

def hx(v):
    # wireshark may export hex like "0x9c40" or decimal like "40000"
    v = v.strip()
    if v.lower().startswith("0x"):
        return int(v, 16)
    return int(v)

rows = []
with open("export.csv", newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        flow = hx(row["ipv6.flow"])
        idx = flow & 0x0fff
        ip_id = hx(row["ip.id"])
        tsval = hx(row["tcp.options.timestamp.tsval"])
        sport = int(row["tcp.srcport"])
        dport = int(row["tcp.dstport"])
        rows.append((idx, ip_id, tsval, sport, dport))

rows.sort(key=lambda x: x[0])
sport = rows[0][3]
dport = rows[0][4]
key = (sport ^ dport) & 0xff

out = bytearray()
for i, (_idx, ip_id, tsval, _s, _d) in enumerate(rows):
    c = (ip_id & 0xff) ^ (tsval & 0xff)
    out.append((c ^ key ^ (i & 0xff)) & 0xff)

text = out.decode("utf-8", errors="replace").strip()
print(text)
print("FLAG =", re.search(r"TDHCTF\\{[^}]+\\}", text).group(0))
```

You should see output like:
- `KEY:<...>`
- `FLAG:TDHCTF{...}`

## Author verifier
You can validate locally using:
- `python3 challenges/net-01-onion-pcap/src/verify_decode.py`


