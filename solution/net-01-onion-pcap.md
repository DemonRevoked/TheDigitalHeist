# net-01-onion-pcap — Walkthrough (Onion PCAP / Header Whispers)

## Goal
Recover **both** values from:
- `challenge-files/net-01-onion-pcap/net-01-onion-pcap.pcap`

Expected output format:
```
KEY:<challenge key>
FLAG:TDHCTF{...}
```

## What you’re looking for (1 paragraph)
Most traffic is noise. The *real* packets have this stack:
`802.1Q (VLAN) → IPv4 → GRE → IPv6 → TCP`

Each packet hides **one ASCII character** in the **low byte** of the outer IPv4 **Identification** field (`ip.id`).  
Packets are **out of order**, but the inner IPv6 **Flow Label is the packet index**, so simple sorting works.

## Step-by-step (Wireshark UI only)

### 1) Open the PCAP
- **File → Open…** → select `net-01-onion-pcap.pcap` → **Open**

### 2) Reduce noise to “GRE inside VLAN”
1. Click the **Display Filter** bar.
2. Paste:
   - `vlan && ip.proto == 47`
3. Press **Enter**.

You should now see packets where the middle pane shows:
`Internet Protocol Version 4 → Generic Routing Encapsulation (GRE) → Internet Protocol Version 6 → TCP`

### 3) Isolate the ONE inner IPv6/TCP conversation (this is the important part)
There are decoy GRE packets. You want the single inner stream that repeats.

#### Option A (fastest): Conversation Filter
1. Click any packet that shows inner **IPv6** and **TCP** in the Packet Details pane.
2. Right‑click that packet in the top packet list.
3. Choose:
   - **Conversation Filter → IPv6**
4. Now add TCP ports too (so it’s one flow, not “all IPv6 between two hosts”):
   - Click a packet → expand **Transmission Control Protocol**
   - Right‑click **Source Port** → **Apply as Filter → Selected**
   - Right‑click **Destination Port** → **Apply as Filter → Selected**

#### Option B (always works): Apply-as-filter from fields
1. Click a packet.
2. In Packet Details, expand **Internet Protocol Version 6**:
   - Right‑click **Source Address** → **Apply as Filter → Selected**
   - Right‑click **Destination Address** → **Apply as Filter → Selected**
3. Expand **Transmission Control Protocol**:
   - Right‑click **Source Port** → **Apply as Filter → Selected**
   - Right‑click **Destination Port** → **Apply as Filter → Selected**

After this, your filter bar should look like:
`vlan && ip.proto == 47 && ipv6.src == ... && ipv6.dst == ... && tcp.srcport == ... && tcp.dstport == ...`

If you did it right, the packet count drops to a **single clean stream**.

### 4) Add the columns you need (2 columns)
Add these as columns (Packet Details → right‑click field → **Apply as Column**):
- **Flow Label**:
  - Expand **Internet Protocol Version 6**
  - Click **Flow Label** → **Apply as Column**
- **IPv4 Identification**:
  - Expand **Internet Protocol Version 4**
  - Click **Identification** → **Apply as Column**

If the bottom bytes pane isn’t visible:
- **View → Packet Bytes**

### 5) Sort into message order
1. Click the **Flow Label** column header to sort.
2. Click again if needed so it’s **ascending**.

### 6) Read the hidden text (character-by-character)
For each packet from top to bottom (now in order):
1. Click the packet.
2. In Packet Details: **Internet Protocol Version 4 → Identification**
3. In **Packet Bytes**:
   - Two bytes are highlighted (IPv4 ID is 2 bytes)
   - Take the **second highlighted byte** (the low byte)
   - Read its ASCII character from the right-side ASCII view and append it to your output

Within a short number of packets you’ll see:
```
KEY:...
FLAG:TDHCTF{...}
```

## Author verifier (optional)
- `python3 challenges/net-01-onion-pcap/src/verify_decode.py`


