# Student Guide — MOB-01 Insecure Notes (Offline APK)

## Objective
Unlock the “note” and recover:
- **KEY** (challenge key)
- **FLAG** (`TDHCTF{...}`)

## Suggested tools
- `jadx` (APK decompiler)

## Intended solve path
1. Install and open the APK.
2. You’ll see an “Unlock note” section that asks for an **access phrase**.
3. Decompile the APK with `jadx`.
4. Search for:
   - `AccessPhraseGate`
   - `MINT-ACCESS`
5. The phrase is split across multiple places:
   - `AndroidManifest.xml` (meta-data)
   - `res/values/strings.xml`
   - `assets/config.txt`
6. Reconstruct the full phrase and enter it in the app.
7. The app reveals the KEY + FLAG.

## Hint ladder
1. The lock is implemented locally.
2. Search for the phrase validation logic.
3. The correct phrase is embedded somewhere in the app code.
