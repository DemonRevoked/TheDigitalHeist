# mob-01 — Walkthrough (Insecure Notes / Easy APK)

## Goal
Unlock the note in the APK and recover:
- **KEY** (challenge key)
- **FLAG** (`TDHCTF{...}`)

## Key insight
The “lock” check is performed **locally** and compares your input to a hidden string embedded in the APK.

## Steps
1. Install and open the APK.
2. The app asks for an **access phrase** in the “Unlock note” section.
3. Decompile the APK with `jadx`.
4. Search for:
   - `AccessPhraseGate`
   - `MINT-ACCESS`
5. The phrase is split across:
   - `AndroidManifest.xml` (meta-data)
   - `res/values/strings.xml`
   - `assets/config.txt`
6. Reconstruct and enter the exact phrase:
   - **`MINT-ACCESS-7429-PROFESSOR`**
8. The app shows **KEY + FLAG**.