The challenge flow:
Decrypt ROT13 → see "Key: <16-byte-key>" and encrypted payload with neccesary details.
Identify encryption method (AES)
Use the 16-byte key directly for AES-128 decryption
Decrypted payload contains BASE64-encoded challenge key and flag
Decode BASE64 to get final values