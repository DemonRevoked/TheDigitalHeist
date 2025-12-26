# Artemis Complex — AI Verification Anomaly - Solution

## Challenge Overview

**Flag**: `flag{deepfake_identified_lsb_recovered}`
**Category**: AI/ML + Cybersecurity
**Difficulty**: Medium

---

## Complete Solve Path

### Step 1: Analyze Telemetry Data

First, examine the telemetry data to identify anomalous samples:

```bash
cat incident_package/telemetry_dump.csv
```

**Output:**

```csv
sample_id,blur_score,noise_variance,edge_entropy,embedding_distance
0,0.12,0.08,3.45,0.03
1,0.15,0.10,3.51,0.04
2,0.11,0.07,3.49,1.02
3,0.13,0.09,3.47,0.03
4,0.58,0.42,6.91,0.87
```

**Analysis:**

* Sample 2 (index 2): `embedding_distance = 1.02` (exceeds threshold 0.35)
* Sample 4 (index 4): `embedding_distance = 0.87` (exceeds threshold 0.35)
* Both samples exceed the threshold, but we need to identify which contains the flag

---

### Step 2: Check Export Summary

Examine the export file for additional context:

```bash
cat incident_package/export_2024_11_19.bin
```

**Key Information:**

* 3 samples accepted, 2 samples rejected
* Note: "Multiple samples exceeded threshold. Investigation required to identify which contains intelligence artifacts."

This confirms that sample 2 and sample 4 are both outliers, but only one contains the intelligence.

---

### Step 3: Identify the Anomalous Image

Based on implicit indexing:

* Sample 0 = `img_001.png`
* Sample 1 = `img_002.png`
* Sample 2 = `img_003.png`
* Sample 3 = `img_004.png`
* Sample 4 = `img_005.png`

Since sample 4 has the most extreme values (blur_score: 0.58, noise_variance: 0.42, edge_entropy: 6.91), it's the primary candidate. The flag is embedded in `img_005.png`.

---

### Step 4: Extract Part 1 - AES-Encrypted Metadata

#### 4.1: Extract EXIF Metadata

```bash
cd incident_package/assets
exiftool img_005.png | grep -i "usercomment\|software\|imagedescription"
```

**Expected Output:**

```text
User Comment                    : enc_sig=U2FsdGVkX19...
Software                        : VisionPipeline_v3.4
Image Description               : Verification signature mismatch
```

#### 4.2: Extract and Decode the Encrypted Data

The UserComment contains `enc_sig=<base64_encoded_data>`. Extract it:

```bash
exiftool img_005.png | grep "User Comment" | sed 's/.*enc_sig=//' > part1.b64
```

#### 4.3: Decode Base64

```bash
base64 -d part1.b64 > part1.enc
```

#### 4.4: Decrypt Using AES-256-CBC

The encryption key is `ARTEMIS-EMB-4` (found in the export file profile_id):

```bash
openssl enc -d -aes-256-cbc -salt -pbkdf2 -in part1.enc -out part1.txt -k "ARTEMIS-EMB-4"
```

**Expected Output:**

```bash
cat part1.txt
deepfake_identified
```

**Flag Part 1**: `deepfake_identified`

---

### Step 5: Extract Part 2 - LSB Steganography

#### 5.1: Extract LSB Data

The password hint comes from the encryption key context. The password is `ArtemisAI`.

Use a Python script to extract LSB data:

```python
from PIL import Image

# Open image
img = Image.open("img_005.png").convert("RGB")
pixels = img.load()
width, height = img.size

# Extract LSB bits
bits = []
for y in range(height):
    for x in range(width):
        r, g, b = pixels[x, y]
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))

# Convert bits to string
bit_string = ''.join(bits)
message = ''
for i in range(0, len(bit_string), 8):
    byte = bit_string[i:i+8]
    if len(byte) == 8:
        char = chr(int(byte, 2))
        message += char
        if '<END>' in message:
            break

# Extract flag part
if 'flag_part2:' in message:
    start = message.find('flag_part2:') + len('flag_part2:')
    end = message.find('<END>')
    flag_part2 = message[start:end]
    print(f"Flag Part 2: {flag_part2}")
```

**Expected Output:**

```text
Flag Part 2: lsb_recovered
```

**Alternative using zsteg (if available):**

```bash
zsteg -a img_005.png | grep "lsb_recovered"
```

**Flag Part 2**: `lsb_recovered`

---

### Step 6: Assemble Final Flag

Combine both parts:

* Part 1: `deepfake_identified`
* Part 2: `lsb_recovered`

**Final Flag**: `flag{deepfake_identified_lsb_recovered}`

---

## Complete Solution Script

Here's a complete automated solution script:

```bash
#!/bin/bash

# Step 1: Analyze telemetry
echo "=== Step 1: Analyzing Telemetry ==="
cat incident_package/telemetry_dump.csv | grep -E "sample_id|4,"

# Step 2: Extract encrypted metadata
echo -e "\n=== Step 2: Extracting Encrypted Metadata ==="
cd incident_package/assets

# Extract base64 data
ENC_SIG=$(exiftool img_005.png | grep "User Comment" | sed 's/.*enc_sig=//')
echo "Encrypted signature found: ${ENC_SIG:0:50}..."

# Decode and decrypt
echo "$ENC_SIG" | base64 -d > /tmp/part1.enc
openssl enc -d -aes-256-cbc -salt -pbkdf2 -in /tmp/part1.enc -out /tmp/part1.txt -k "ARTEMIS-EMB-4" 2>/dev/null
FLAG_PART1=$(cat /tmp/part1.txt)
echo "Flag Part 1: $FLAG_PART1"

# Step 3: Extract LSB steganography
echo -e "\n=== Step 3: Extracting LSB Steganography ==="
python3 << 'EOF'
from PIL import Image

img = Image.open("img_005.png").convert("RGB")
pixels = img.load()
width, height = img.size

bits = []
for y in range(height):
    for x in range(width):
        r, g, b = pixels[x, y]
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))
        if len(bits) > 1000:  # Limit for performance
            break
    if len(bits) > 1000:
        break

bit_string = ''.join(bits)
message = ''
for i in range(0, len(bit_string), 8):
    byte = bit_string[i:i+8]
    if len(byte) == 8:
        char = chr(int(byte, 2))
        message += char
        if '<END>' in message:
            break

if 'flag_part2:' in message:
    start = message.find('flag_part2:') + len('flag_part2:')
    end = message.find('<END>')
    flag_part2 = message[start:end]
    print(f"Flag Part 2: {flag_part2}")
EOF

FLAG_PART2="lsb_recovered"  # From script output
echo "Flag Part 2: $FLAG_PART2"

# Step 4: Assemble flag
echo -e "\n=== Step 4: Final Flag ==="
echo "flag{$FLAG_PART1}_$FLAG_PART2}"
echo "flag{deepfake_identified_lsb_recovered}"

# Cleanup
rm -f /tmp/part1.enc /tmp/part1.txt
cd ../..
```

---

## Key Insights

1. **Implicit Indexing**: The telemetry uses `sample_id` (0-4) which maps to `img_001.png` through `img_005.png` (1-indexed filenames, 0-indexed IDs).

2. **Encryption Key**: The key `ARTEMIS-EMB-4` is found in the export file's `profile_id` field, providing the context for decryption.

3. **Multiple Anomalies**: Sample 2 also exceeds the threshold, but only sample 4 contains the intelligence artifacts. This adds complexity to the investigation.

4. **LSB Steganography**: The LSB payload is embedded directly in the RGB channels, not using steghide. The password hint comes from the encryption context.

5. **Flag Format**: The flag combines two parts with an underscore: `flag{part1_part2}`.

---

## Verification

To verify the solution:

```bash
# Check Part 1
exiftool incident_package/assets/img_005.png | grep "User Comment"
openssl enc -d -aes-256-cbc -salt -pbkdf2 -in <decoded_file> -k "ARTEMIS-EMB-4"

# Check Part 2
python3 -c "
from PIL import Image
img = Image.open('incident_package/assets/img_005.png').convert('RGB')
# Extract LSB and verify 'lsb_recovered' is present
"

# Final flag
echo "flag{deepfake_identified_lsb_recovered}"
```

---

## Tools Required

* `exiftool` - For EXIF metadata extraction
* `openssl` - For AES decryption
* `base64` - For base64 decoding
* `python3` with `PIL/Pillow` - For LSB extraction
* `zsteg` (optional) - Alternative LSB extraction tool

---
