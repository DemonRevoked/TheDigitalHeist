# ai-01-artemis — Walkthrough

## Goal
Find the fake staff image and recover the hidden flag.

## Steps
1. **Download the package**
   - Download `incident_package.zip`.
   - Unzip it.

2. **Find the “weird” sample**
   - Open `telemetry_dump.csv`.
   - Look for the row with a big `embedding_distance`.
   - That row points to the suspicious image.
   - In this challenge, it matches `assets/img_005.png`.

3. **Read hidden metadata (optional but helpful)**
   - Run:
     - `exiftool assets/img_005.png`
   - You will see a `UserComment` that includes `enc_sig=...`

4. **Pull the hidden text from the image (LSB)**
   - The real secret is stored in the lowest bits (LSB) of `img_005.png`.
   - Extract the hidden message until you see `<END>`.
   - You will get:
     - `flag_part2:{lsb_recovered}`

5. **Build the final flag**
   - Final flag format:
     - `flag{deepfake_identified_<flag_part2>}`
   - So the final flag is:
     - **flag{deepfake_identified_lsb_recovered}**

## Extra
`assets/img_002.png` also contains a `challenge_key:...` value in metadata (use `exiftool`).

