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
### 0) Find the method hint inside the PCAP (operator note)
1. Apply a filter:
   - `tcp.port == 80`
2. Right‑click a packet → **Follow → TCP Stream**
3. In the plaintext stream you should see this exact hint:
   - `lengths->base32, v=(L-480)/7 | A-Z2-7.`

This tells you the decode rule and the Base32 alphabet.

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

#### CSV Formula Method (Excel/Google Sheets)

After exporting the CSV from Wireshark, assume:
- Column A contains the packet number/row
- Column B contains `tls.record.length` (or the column name where TLS record lengths are stored)

**Step 1: Filter valid lengths**
Add a new column (e.g., Column C) to check if the length fits the encoding:
```excel
=IF(AND(B2>=480, MOD(B2-480, 7)=0, (B2-480)/7>=0, (B2-480)/7<32), "VALID", "")
```

**Step 2: Calculate Base32 index**
Add Column D to calculate the Base32 value index:
```excel
=IF(C2="VALID", (B2-480)/7, "")
```

**Step 3: Map to Base32 character**
Add Column E to convert index to Base32 character:
```excel
=IF(D2<>"", MID("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", D2+1, 1), "")
```

**Step 4: Concatenate Base32 string**
In a separate cell (e.g., F1), concatenate all valid Base32 characters:
```excel
=TEXTJOIN("", TRUE, E:E)
```

**Step 5: Decode Base32 to text**
In another cell (e.g., G1), decode the Base32 string. For Google Sheets:
```excel
=FROM_BASE32(F1)
```

For Excel (requires manual Base32 decode or use online tool):
- Copy the Base32 string from F1
- Use an online Base32 decoder or Python: `base64.b32decode(string + "=" * padding)`

**Alternative: Single Formula Approach (Google Sheets)**

If you want to do it all in one go, assuming Column B has the lengths:

```excel
=TEXTJOIN("", TRUE, ARRAYFORMULA(IF((B:B>=480)*(MOD(B:B-480, 7)=0)*((B:B-480)/7>=0)*((B:B-480)/7<32), MID("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", (B:B-480)/7+1, 1), "")))
```

Note: Using `*` instead of `AND()` in ARRAYFORMULA because `AND()` doesn't work element-wise in arrays.

Then decode with:
```excel
=FROM_BASE32(<result_cell>)
```

**Python Script Method**

Save your CSV export and use this Python script:

```python
import csv
import base64

BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

# Read CSV - adjust column name/index as needed
lengths = []
with open('exported_packets.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Try different possible column names
        length = None
        for col in ['tls.record.length', 'Length', 'TLS Record Length']:
            if col in row and row[col]:
                try:
                    length = int(row[col])
                    break
                except:
                    pass
        if length:
            lengths.append(length)

# Filter and decode
symbols = []
for L in lengths:
    if L >= 480 and (L - 480) % 7 == 0:
        v = (L - 480) // 7
        if 0 <= v < 32:
            symbols.append(BASE32_ALPHABET[v])

# Decode Base32
b32_string = ''.join(symbols)
# Add padding if needed
pad = "=" * ((8 - (len(b32_string) % 8)) % 8)
decoded = base64.b32decode(b32_string + pad).decode('utf-8')
print(decoded)
```

**Manual Method**
For each extracted TLS record length \(L\):
1. Keep only values that fit the encoding:
   - \(L = 480 + 7v\) where \(v \in [0, 31]\)
   - Check: \(L \geq 480\) and \((L - 480) \bmod 7 = 0\)
2. Convert \(v\) to a Base32 symbol using:
   - \(v = (L - 480) / 7\)
   - Map to: `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` (index 0-31)
3. Base32‑decode the resulting string to plaintext.

You should see:
- `KEY: ...`
- `FLAG: TDHCTF{...}`

## Author verifier
You can validate locally using:
- `python3 challenges/net-02-doh-rhythm/src/verify_decode.py`


