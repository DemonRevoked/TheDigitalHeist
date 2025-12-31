## crypto-01-intercepted-comms — Walkthrough (ROT13 → AES-CBC → Base64)

### Goal
Decrypt `intercepted_message.txt` to recover **both**:
- `KEY:<challenge key>`
- `FLAG:TDHCTF{intercepted_comms_decrypted}`

### What’s going on (high level)
- The whole file is **ROT13**.
- Inside the ROT13-decoded text you’ll find:
  - a **16-character AES key**
  - a single-line **Base64 ciphertext** under `ENCRYPTED PAYLOAD:`
- Decrypt ciphertext using **AES-128-CBC**, with:
  - **IV** = 16 zero bytes
  - **PKCS#7 padding**
- The decrypted plaintext contains **two Base64 lines**:
  1) Base64(challenge key)  
  2) Base64(flag)

### Shell solve (copy/paste)
From repo root:

```bash
cd /home/demon/TheDigitalHeist/challenge-files/crypto-01-intercepted-comms
FILE=intercepted_message.txt

# 1) ROT13 decode the entire file
ROT13="$(tr 'A-Za-z' 'N-ZA-Mn-za-m' < \"$FILE\")"

# 2) Extract the 16-byte AES key
AES_KEY="$(printf '%s' \"$ROT13\" | grep -oP 'The key to unlock this is: \\K.{16}')"
echo \"AES_KEY=$AES_KEY\"

# 3) Extract the Base64 ciphertext line under ENCRYPTED PAYLOAD:
CT_B64="$(printf '%s' \"$ROT13\" | awk '/^ENCRYPTED PAYLOAD:/{getline; print; exit}' | tr -d '\\r\\n')"

# 4) IMPORTANT: pad Base64 for openssl (openssl is stricter than Python)
CT_B64_PADDED=\"$CT_B64$(python3 - <<'PY'\nimport sys\ns=sys.stdin.read().strip()\nprint('='*((4-len(s)%4)%4), end='')\nPY\n<<<\"$CT_B64\")\"

# 5) AES decrypt (CBC, IV = 16 null bytes)
KEY_HEX=\"$(printf '%s' \"$AES_KEY\" | xxd -p -c 256)\"
IV_HEX=\"00000000000000000000000000000000\"
PLAINTEXT_B64_LINES=\"$(printf '%s' \"$CT_B64_PADDED\" | openssl enc -aes-128-cbc -d -K \"$KEY_HEX\" -iv \"$IV_HEX\" -base64 -A -nosalt)\"

# 6) Decode the two Base64 lines to final KEY + FLAG
CHALLENGE_KEY=\"$(printf '%s' \"$PLAINTEXT_B64_LINES\" | sed -n '1p' | base64 -d)\"\nFLAG=\"$(printf '%s' \"$PLAINTEXT_B64_LINES\" | sed -n '2p' | base64 -d)\"\n\necho \"KEY:$CHALLENGE_KEY\"\necho \"FLAG:$FLAG\"\n+```

### Python solve (no third‑party deps; uses `openssl` for AES)
Run from the directory containing `intercepted_message.txt`:

```python
import base64, re, subprocess, pathlib

data = pathlib.Path("intercepted_message.txt").read_text()
rot = data.translate(str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
))

aes_key = re.search(r"The key to unlock this is: (.{16})", rot).group(1)
ct_b64 = re.search(r"ENCRYPTED PAYLOAD:\\n([^\\n]+)", rot).group(1).strip()
ct_b64 += "=" * ((4 - (len(ct_b64) % 4)) % 4)  # openssl wants padded base64

key_hex = aes_key.encode().hex()
iv_hex = "00" * 16

pt = subprocess.check_output(
    ["openssl", "enc", "-aes-128-cbc", "-d", "-K", key_hex, "-iv", iv_hex, "-base64", "-A", "-nosalt"],
    input=ct_b64.encode(),
)

line1, line2 = pt.decode().strip().splitlines()
challenge_key = base64.b64decode(line1).decode()
flag = base64.b64decode(line2).decode()

print("KEY:" + challenge_key)
print("FLAG:" + flag)
```

### CyberChef solve (easy UI flow)
Use [CyberChef](https://gchq.github.io/CyberChef/) (or your self-hosted instance).

1) Paste the contents of `intercepted_message.txt` into **Input**.

2) Add these operations (in order):
- **ROT13**
- **Extract** (to grab the AES key)
  - **Regex**: `The key to unlock this is: (.{16})`
  - **Group**: `1`
  - Copy the extracted 16-char key somewhere (you will paste it into AES below).
- **Extract** (to grab the ciphertext)
  - **Regex**: `ENCRYPTED PAYLOAD:\n([A-Za-z0-9+/=]+)`
  - **Group**: `1`
  - This output is the Base64 ciphertext.

3) With the ciphertext selected as your working input, add:
- **AES Decrypt**
  - **Mode**: `CBC`
  - **Key**: paste the 16-character key you extracted
  - **Key format**: `UTF8`
  - **IV**: `00000000000000000000000000000000`
  - **IV format**: `Hex`
  - **Input**: `Base64`
  - **Padding**: `PKCS7`

4) The AES output will be **two Base64 lines**. Decode them:
- **Split** (separator: newline) OR just decode line-by-line
- **From Base64** (run on each line)

You should end up with:
- `KEY:<challenge key>`
- `FLAG:TDHCTF{intercepted_comms_decrypted}`

