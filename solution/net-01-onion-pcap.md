# net-01-onion-pcap — Walkthrough (DNS Tunneling Exfiltration)

## Goal
Recover **both** values from:
- `challenge-files/net-01-onion-pcap/net-01-onion-pcap.pcap`

Expected output format:
```
KEY:<challenge key>
FLAG:TDHCTF{...}
```

## What you're looking for (1 paragraph)
This challenge demonstrates **DNS tunneling**—a real-world exfiltration technique used by malware and attackers. Data is encoded in DNS query names (subdomain labels) using Base64 URL-safe encoding. The rogue engineer's client IP (`10.0.5.42`) sends DNS queries where each query's subdomain contains a Base64 chunk of the exfiltrated data. Extract all DNS queries from the signal client, concatenate the Base64 chunks, and decode to recover the flag.

## Real-World Context
DNS tunneling is commonly used by:
- **Malware**: Iodine, dnscat2, DNSStager, Cobalt Strike DNS beacons
- **APT groups**: To bypass network restrictions and exfiltrate data
- **Red teams**: For command and control (C2) communication

The technique works because DNS is often allowed through firewalls, making it an attractive covert channel.

## Step-by-step (Wireshark UI only)

### 1) Open the PCAP
- **File → Open…** → select `net-01-onion-pcap.pcap` → **Open**

### 2) Filter for DNS traffic
1. Click the **Display Filter** bar.
2. Paste:
   - `dns`
3. Press **Enter**.

You should now see DNS query packets.

### 3) Identify the signal client
The rogue engineer uses a specific client IP. Look for DNS queries from:
- `10.0.5.42` (the signal client)

Apply a filter:
- `dns && ip.src == 10.0.5.42`

Alternatively, you can identify it by:
- Looking for DNS queries to `*.blueprint.professor.royalmint.local` (the exfiltration pattern + storyline hint)
- Filter: `dns.qry.name contains "blueprint.professor.royalmint.local"`

### 4) Extract DNS query names
1. Right-click a DNS query packet → **Follow → UDP Stream** (optional, for context)
2. To extract query names systematically:
   - **File → Export Packet Dissections → As CSV…**
   - Make sure `dns.qry.name` column is included
   - Or manually note the query names from the Packet Details pane

3. In Packet Details, expand **Domain Name System (query)**:
   - Look for **Name** field (e.g., `xxxxx.blueprint.professor.royalmint.local`)
   - The Base64 chunk is the first label (before `.blueprint.`)

### 5) Extract and decode Base64 chunks

#### Manual Method
For each DNS query from the signal client:
1. Extract the first subdomain label (the Base64 chunk)
   - Example: `s0vzomfiyy2q.blueprint.professor.royalmint.local` → `s0vzomfiyy2q`
2. Collect all chunks in order (you may need to sort by timestamp)
3. Concatenate: `s0vzomfiyy2q` + `abc123def456` + `ghi789jkl012` + ... = `s0vzomfiyy2qabc123def456ghi789jkl012...`
4. Decode the Base64 string (URL-safe) to get the original message

#### Python Script Method

```python
import pyshark
import base64

# Open the PCAP
cap = pyshark.FileCapture('net-01-onion-pcap.pcap', display_filter='dns && ip.src == 10.0.5.42 && dns.qry.name contains "blueprint.professor.royalmint.local"')

chunks = []
for packet in cap:
    try:
        qname = packet.dns.qry_name
        # Extract the Base64 chunk (first label before .blueprint.)
        if '.blueprint.professor.royalmint.local' in qname:
            chunk = qname.split('.')[0]  # Keep case as-is for Base64
            chunks.append(chunk)
    except:
        pass

# Sort by timestamp if needed (packets might be out of order)
# For this challenge, you can also sort by packet number

# Concatenate and decode (URL-safe Base64)
b64_string = ''.join(chunks)
# Add padding if needed
pad = "=" * ((4 - (len(b64_string) % 4)) % 4)
decoded = base64.urlsafe_b64decode(b64_string + pad).decode('utf-8')
print(decoded)
```

#### Wireshark + Manual Decode
1. Filter: `dns && ip.src == 10.0.5.42 && dns.qry.name contains "blueprint.professor.royalmint.local"`
2. Export DNS query names to a text file
3. Extract the first label from each query name
4. Use an online Base64 decoder or Python:
   ```python
   import base64
   b64_string = "s0vzomfiyy2qabc123..."  # Your concatenated chunks
   pad = "=" * ((4 - (len(b64_string) % 4)) % 4)
   decoded = base64.urlsafe_b64decode(b64_string + pad).decode('utf-8')
   print(decoded)
   ```

### 6) Verify the output
You should see:
```
KEY:<challenge key>
FLAG:TDHCTF{...}
```

## Author verifier (optional)
- `python3 challenges/net-01-onion-pcap/src/verify_decode.py`

## Learning Points
- **DNS tunneling** is a real attack technique used in the wild
- Attackers encode data in DNS query names to bypass network restrictions
- Base64 URL-safe encoding is DNS-compatible (uses - and _ instead of + and /)
- Detection requires analyzing DNS query patterns and identifying anomalous subdomains
- Real-world tools: Iodine, dnscat2, DNSStager, Cobalt Strike
