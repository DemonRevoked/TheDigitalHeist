# Crypto-01 Challenge - Complete Fix Summary

## Overview
The crypto-01-intercepted-comms challenge has been fixed with the correct architecture:
- **Hardcoded AES decryption key** (shown in the message)
- **Dynamic challenge key** (from `keys/crypto-01.key`)
- **Hardcoded flag** (always `TDHCTF{intercepted_comms_decrypted}`)

## Issues Fixed

### 1. IV Mismatch (Original Issue)
**Problem:** The IV was set to ASCII '0' characters (`b'0000000000000000'`) instead of null bytes.
**Fix:** Changed to `b'\x00' * 16` (true null bytes)

### 2. Key Architecture (New Requirement)
**Problem:** The AES key was derived from the challenge key, making it dynamic.
**Fix:** Separated into two distinct keys:
- **Hardcoded AES Key:** `HEISTFgjXbeZzNk6` (for decryption, shown in message)
- **Dynamic Challenge Key:** From `keys/crypto-01.key` file (part of the payload)

## File Changes

### 1. `challenges/crypto-01-intercepted-comms/src/encrypt.py`

**Changed:**
```python
# OLD: Dynamic AES key derived from challenge key
key_part = challenge_key[:11] if len(challenge_key) >= 11 else challenge_key + 'X' * (11 - len(challenge_key))
aes_key = ("HEIST" + key_part)[:16]

# NEW: Hardcoded AES key + separate challenge key
aes_key = "HEISTFgjXbeZzNk6"  # Hardcoded for decryption
challenge_key = os.environ['CHALLENGE_KEY']  # From keys/crypto-01.key
flag = "TDHCTF{intercepted_comms_decrypted}"  # Hardcoded
```

**Also fixed:**
```python
# OLD: ASCII '0' characters
iv = b'0000000000000000'

# NEW: True null bytes
iv = b'\x00' * 16
```

### 2. `challenge-files/crypto-01-intercepted-comms/intercepted_message.txt`

Regenerated with:
- Hardcoded AES key: `HEISTFgjXbeZzNk6` (ROT13 encoded in message)
- Encrypted payload containing:
  - Challenge key: `FgjXbeZzNk6yFo1ECcRqaPiwrJ4vGz9TsMOJXR5E` (from `keys/crypto-01.key`)
  - Flag: `TDHCTF{intercepted_comms_decrypted}`

## Solution Path

### Step 1: ROT13 Decrypt
Apply ROT13 to the intercepted message to reveal:
- The hardcoded AES key: `HEISTFgjXbeZzNk6`
- The encrypted payload
- Hints about AES-CBC, 16-byte blocks, null byte IV

### Step 2: AES-128-CBC Decryption
Decrypt the payload using:
- **Key:** `HEISTFgjXbeZzNk6` (from the message)
- **IV:** 16 null bytes (`\x00` * 16 or `00000000000000000000000000000000`)
- **Mode:** CBC

### Step 3: Base64 Decode
The decrypted payload contains two base64-encoded strings:
1. Challenge Key (base64) → decode to get the actual challenge key
2. Flag (base64) → decode to get `TDHCTF{intercepted_comms_decrypted}`

## Verification

```bash
# Complete solution
cat intercepted_message.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m' | grep -A 1 "ENCRYPTED PAYLOAD:" | tail -1 | \
  openssl enc -aes-128-cbc -d -K 484549535446676a5862655a7a4e6b36 -iv 00000000000000000000000000000000 -base64

# Output:
# RmdqWGJlWnpOazZ5Rm8xRUNjUnFhUGl3cko0dkd6OVRzTU9KWFI1RQ==
# VERIQ1RGe2ludGVyY2VwdGVkX2NvbW1zX2RlY3J5cHRlZH0=

# Decode base64:
echo "RmdqWGJlWnpOazZ5Rm8xRUNjUnFhUGl3cko0dkd6OVRzTU9KWFI1RQ==" | base64 -d
# Output: FgjXbeZzNk6yFo1ECcRqaPiwrJ4vGz9TsMOJXR5E

echo "VERIQ1RGe2ludGVyY2VwdGVkX2NvbW1zX2RlY3J5cHRlZH0=" | base64 -d
# Output: TDHCTF{intercepted_comms_decrypted}
```

## Key Architecture Summary

| Key Type | Value | Purpose | Source |
|----------|-------|---------|--------|
| **AES Decryption Key** | `HEISTFgjXbeZzNk6` | Decrypt the payload | Hardcoded in script, shown in message |
| **Challenge Key** | `FgjXbeZzNk6yFo1ECcRqaPiwrJ4vGz9TsMOJXR5E` | Part of the solution | From `keys/crypto-01.key` file |
| **Flag** | `TDHCTF{intercepted_comms_decrypted}` | CTF flag | Hardcoded in script |

## Challenge Difficulty
The challenge remains **EASY** level:
1. ROT13 decryption (classical cipher, frequency analysis)
2. AES-CBC understanding (standard encryption)
3. Base64 encoding/decoding (common encoding)
4. Following narrative hints (reading comprehension)

## Status
✅ **COMPLETE** - All issues fixed and verified
- ✅ IV uses proper null bytes
- ✅ Hardcoded AES key for decryption
- ✅ Dynamic challenge key from file
- ✅ Hardcoded flag
- ✅ Clean decryption with no garbled output

