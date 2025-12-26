# re-02-evidence-tampering — Walkthrough

## Goal
Find the **one number** that makes the program print:
`Timeline rewrite validated.`

## Steps
1. **Open the binary in Ghidra**
   - Analyze it (default options).

2. **Find the success text**
   - Search → For Strings
   - Find: `Timeline rewrite validated.`
   - Press **X** (references) and open the code that uses it.

3. **Find the math check**
   - In the decompiler, find the line that reads your input (it uses `strtoull`).
   - You should see this logic:
     - `(uVar10 ^ 0x5a5a5a5a5a5a5a5a) - 0x1111110a` must equal the target.

4. **Find the target value**
   - The program decrypts 10 bytes from a data address, then does `strtoull(...)`.
   - The decrypted bytes do **not** start with digits, so `strtoull` returns **0**.
   - So the target is **0**.

5. **Solve**
   - If target is 0, then:
     - `uVar10 = 0x1111110a ^ 0x5a5a5a5a5a5a5a5a`
   - Result:
     - Hex: `0x5a5a5a5a4b4b4b50`
     - Decimal: **6510615555174255440**

6. **Submit**
   - Run the program and enter:
     - **6510615555174255440**

