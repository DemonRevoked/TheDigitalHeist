# re-01-confession-app — Walkthrough

## Goal
Find the **passphrase** inside the `confession_app` program.

## Steps
1. **Open the binary**
   - Run `strings confession_app | less`
   - If you don’t see the answer, open it in **Ghidra**.

2. **Find the encoded text**
   - In Ghidra, find the function that checks your input.
   - You will see a call that points to some data bytes (an address + a length).

3. **Copy the bytes**
   - Press **G** in Ghidra and go to the shown address.
   - Select the number of bytes shown in the call.
   - Copy them as hex / byte string.

4. **Decode**
   - The code does an **XOR decode**.
   - After XOR, you get this text:
     - `su ot delaever won si noitacol yawetag krowten eTh`

5. **Reverse it**
   - Reverse the text (because the program reverses before compare).
   - Final passphrase:
     - **The network gateway location is now revealed to us**

6. **Submit**
   - Run the program and enter the passphrase.

