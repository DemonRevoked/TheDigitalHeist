# net-02-doh-rhythm — Walkthrough (HTTP Header Exfiltration)

## Goal
Recover **both** values from `challenge-files/net-02-doh-rhythm/net-02-doh-rhythm.pcap`:
- `KEY: <challenge key>`
- `FLAG: TDHCTF{...}`

## Key insight
You **cannot** (and do not need to) decrypt anything. The flag leaks through **HTTP headers**:
- Identify the signal HTTP flow (specific client IP)
- Extract Base64-encoded chunks from HTTP request headers (User-Agent field)
- Concatenate chunks → Base64 decode → recover flag

## Real-World Context
HTTP header exfiltration is commonly used by:
- **Malware**: To exfiltrate data through HTTP requests that look like normal web traffic
- **APT groups**: To bypass Data Loss Prevention (DLP) systems
- **Red teams**: For covert data exfiltration during penetration tests

The technique works because:
- HTTP headers are often not deeply inspected by security tools
- User-Agent and custom headers can contain arbitrary data
- Traffic looks like normal web browsing to casual inspection

## Solve outline

### 0) Find the method hint (optional)
The challenge name "DoH Rhythm" is a red herring—this is actually HTTP header exfiltration, not DNS-over-HTTPS.

### 1) Find the signal HTTP flow
1. Open `net-02-doh-rhythm.pcap` in Wireshark.
2. Apply a filter:
   - `http && ip.src == 10.13.37.10`
3. Alternatively, look for HTTP requests to `metrics.internal.corp`:
   - `http.host contains "metrics.internal.corp"`

### 2) Extract HTTP headers
1. Right-click an HTTP request packet → **Follow → HTTP Stream**
2. Look at the HTTP request headers, specifically the **User-Agent** field
3. You should see patterns like:
   - `User-Agent: Mozilla/5.0 (compatible; ExfilChunk-<base64_chunk>)`

### 3) Extract Base64 chunks from User-Agent headers

#### Manual Method (Wireshark UI)
1. Filter: `http && ip.src == 10.13.37.10 && http.user_agent contains "ExfilChunk-"`
2. For each HTTP request:
   - Expand **Hypertext Transfer Protocol**
   - Find **User-Agent** field
   - Extract the Base64 chunk after `ExfilChunk-`
   - Example: `ExfilChunk-S0VZOmFiY2RlZmdoaWprbG1ub3Bx` → `S0VZOmFiY2RlZmdoaWprbG1ub3Bx`

#### Export Method
1. Filter: `http && ip.src == 10.13.37.10 && http.user_agent contains "ExfilChunk-"`
2. **File → Export Packet Dissections → As CSV…**
3. Ensure `http.user_agent` column is included
4. Extract chunks from the CSV

#### Python Script Method

```python
import pyshark
import base64
import re

# Open the PCAP
cap = pyshark.FileCapture('net-02-doh-rhythm.pcap', display_filter='http && ip.src == 10.13.37.10')

chunks = []
for packet in cap:
    try:
        user_agent = packet.http.user_agent
        # Extract Base64 chunk from User-Agent
        match = re.search(r'ExfilChunk-([A-Za-z0-9_-]+)', user_agent)
        if match:
            chunk = match.group(1)
            chunks.append(chunk)
    except:
        pass

# Concatenate and decode
b64_string = ''.join(chunks)
# Add padding if needed
pad = "=" * ((4 - (len(b64_string) % 4)) % 4)
decoded = base64.urlsafe_b64decode(b64_string + pad).decode('utf-8')
print(decoded)
```

#### Wireshark + Manual Decode
1. Filter: `http && ip.src == 10.13.37.10 && http.user_agent contains "ExfilChunk-"`
2. Export HTTP User-Agent headers to a text file
3. Extract Base64 chunks using regex: `ExfilChunk-([A-Za-z0-9_-]+)`
4. Concatenate all chunks
5. Decode Base64 (URL-safe):
   ```python
   import base64
   b64_string = "S0VZOmFiY2RlZmdoaWprbG1ub3Bx..."  # Your concatenated chunks
   pad = "=" * ((4 - (len(b64_string) % 4)) % 4)
   decoded = base64.urlsafe_b64decode(b64_string + pad).decode('utf-8')
   print(decoded)
   ```

### 4) Decode Base64 to recover flag

After extracting all Base64 chunks and concatenating them:

```python
import base64

# Your concatenated Base64 string
b64_string = "S0VZOmFiY2RlZmdoaWprbG1ub3Bx..."

# Add padding if needed (Base64 requires length to be multiple of 4)
pad = "=" * ((4 - (len(b64_string) % 4)) % 4)

# Decode (using URL-safe Base64 as used in HTTP headers)
decoded = base64.urlsafe_b64decode(b64_string + pad).decode('utf-8')
print(decoded)
```

You should see:
- `KEY: <challenge key>`
- `FLAG: TDHCTF{...}`

## Alternative: Using tshark command line

```bash
# Extract User-Agent headers
tshark -r net-02-doh-rhythm.pcap \
  -Y 'http.request && ip.src == 10.13.37.10 && http.user_agent contains "ExfilChunk-"' \
  -T fields -e http.user_agent | \
  grep -oP 'ExfilChunk-\K[A-Za-z0-9_-]+' | \
  tr -d '\n' > chunks.txt

# Decode (Python one-liner)
python3 -c "import base64; s=open('chunks.txt').read().strip(); pad='='*((4-len(s)%4)%4); print(base64.urlsafe_b64decode(s+pad).decode())"
```

## Author verifier
You can validate locally using:
- `python3 challenges/net-02-doh-rhythm/src/verify_decode.py`

## Learning Points
- **HTTP header exfiltration** is a real attack technique used in the wild
- Attackers encode data in HTTP headers (User-Agent, Referer, custom headers) to bypass DLP
- Base64 encoding is commonly used because it's header-safe
- Detection requires analyzing HTTP header patterns and identifying anomalous values
- Real-world examples: APT28, APT29, various banking trojans use this technique
- Security controls: DLP systems should inspect HTTP headers, not just payloads
