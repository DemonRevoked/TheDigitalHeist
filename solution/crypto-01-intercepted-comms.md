# crypto-01-intercepted-comms — Walkthrough

## Goal
Decrypt `intercepted_message.txt` to get the **key** and the **flag**.

## Steps
1. **Open the file**
   - Read `intercepted_message.txt`.

2. **Decode ROT13**
   - The whole message is ROT13.
   - After ROT13, you will see:
     - An AES key line: `The key to unlock this is: ...`
     - A big `ENCRYPTED PAYLOAD:` block (Base64 text)

3. **Decrypt the payload with AES-128**
   - Use the 16‑character key you found.
   - The IV is **16 zero bytes**.
   - Mode is **CBC**.
   - Decrypt the Base64 ciphertext.

4. **Decode Base64**
   - The AES output is two Base64 lines.
   - Decode both lines.
   - You now have:
     - The challenge key
     - The flag

