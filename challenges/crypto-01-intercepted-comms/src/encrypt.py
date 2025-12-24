#!/usr/bin/env python3
"""
The Intercepted Message - CRYPTO-01-EASY
Two-part encryption: Caesar hint + AES encrypted payload

ENCRYPTION ORDER (matches challenge3.md):
1. BASE64 encode challenge key and flag
2. AES encrypt the BASE64-encoded payload (produces Base64-encoded ciphertext)
3. Create message with key and encrypted payload
4. ROT13 encrypt entire message

DECRYPTION ORDER (user must follow):
1. Decrypt ROT13 → see "Key: <16-byte-key>" and encrypted payload with necessary details
2. Identify encryption method (AES from hints)
3. Use the 16-byte key directly for AES-128 decryption
4. Decrypted payload contains BASE64-encoded challenge key and flag
5. Decode BASE64 to get final values
"""

import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def caesar_encrypt(text, shift):
    """Apply Caesar cipher with given shift"""
    result = []
    for char in text:
        if char.isupper():
            result.append(chr((ord(char) - 65 + shift) % 26 + 65))
        elif char.islower():
            result.append(chr((ord(char) - 97 + shift) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)

def aes_encrypt(plaintext, key):
    """AES encryption in CBC mode - simplified for standard tools"""
    # Key should already be 16 bytes
    key_bytes = key.encode('utf-8')[:16]
    if len(key_bytes) < 16:
        key_bytes = key_bytes.ljust(16, b'X')
    
    # Use a simple fixed IV (16 bytes) - all zeros for simplicity
    iv = b'\x00' * 16  # 16 null bytes (true zeros)
    
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    return base64.b64encode(ciphertext).decode('utf-8')

def main():
    # HARDCODED AES KEY - Used for decryption (shown in the message after ROT13)
    # This key is static and used to decrypt the payload
    aes_key = "HEISTFgjXbeZzNk6"  # Exactly 16 bytes for AES-128
    
    # Get the CHALLENGE KEY from environment (from keys/crypto-01.key file)
    # This is the dynamic key that changes per deployment
    if 'CHALLENGE_KEY' in os.environ:
        challenge_key = os.environ['CHALLENGE_KEY']
    else:
        challenge_key = "offline-default-crypto01"
    
    # HARDCODED FLAG - Always the same
    flag = "TDHCTF{intercepted_comms_decrypted}"
    
    # ENCRYPTION ORDER (matching challenge3.md flow):
    # Step 1: Create BASE64 encoded challenge key and flag
    #         (This will be inside the AES-encrypted payload)
    challenge_key_b64 = base64.b64encode(challenge_key.encode()).decode()
    flag_b64 = base64.b64encode(flag.encode()).decode()
    
    # Step 2: AES encrypt the BASE64 encoded key and flag
    #         (Result: Base64-encoded ciphertext that contains BASE64-encoded challenge key and flag)
    payload = f"{challenge_key_b64}\n{flag_b64}"
    aes_encrypted_payload = aes_encrypt(payload, aes_key)  # Returns Base64-encoded ciphertext
    
    # Step 3: Create message containing key and encrypted payload
    #         (After ROT13 decrypt, user sees key and encrypted payload)
    #         Story-driven with subtle technical hints embedded naturally
    message = f"""=== INTERCEPTED TRANSMISSION ===
FROM: UNKNOWN OPERATIVE
TO: HEIST COORDINATOR
STATUS: ENCRYPTED

MESSAGE:
Professor, I've secured the intel using our standard protocol - the same method we used for the Royal Mint blueprints. Each piece of information is locked in blocks of sixteen, chained together like the vault doors at the Bank of Spain. Nothing stands alone - every block depends on what came before it.

The initialization sequence starts from zero - a clean slate, sixteen zeros to begin the chain. This is how we've always done it, Professor. Standard padding applied, just like you taught us.

The key to unlock this is: {aes_key}
Remember, it must be exactly sixteen characters - no more, no less. That's the size of our blocks, Professor. One hundred twenty-eight bits per block, sixteen bytes each.

The payload below has been encoded using our base transmission format - you'll need to decode it first before applying the decryption key. Think of it like the Professor's plan: first you decode the message, then you break the cipher.

The critical information is locked inside. Use the key above with the zero initialization sequence to reveal what we've discovered about the Directorate's operations.

ENCRYPTED PAYLOAD:
{aes_encrypted_payload}

Remember: decode first, then decrypt. The truth is locked in those blocks, Professor.

END TRANSMISSION"""
    
    # Step 4: ROT13 encrypt the ENTIRE message (including the encrypted data)
    #         (User must decrypt ROT13 first to see key and encrypted payload)
    caesar_shift = 13  # ROT13
    encrypted_message = caesar_encrypt(message, caesar_shift)
    
    # Write output file
    output_path = '/challenge-files/crypto-01-intercepted-comms/intercepted_message.txt'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(encrypted_message)
    
    print(f"[+] Challenge file generated: {output_path}")
    print(f"[+] AES Key: {aes_key} (16 bytes for AES-128)")
    print(f"[+] Caesar shift: {caesar_shift}")
    print(f"[+] Challenge Key: {challenge_key}")
    print(f"[+] Flag: {flag}")

if __name__ == '__main__':
    main()

