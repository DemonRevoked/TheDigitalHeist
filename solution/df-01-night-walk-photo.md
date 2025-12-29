# df-01-night-walk-photo — Walkthrough (The Night Walk Photo)

## Goal
Recover **both** values from:
- `challenge-files/df-01-night-walk-photo/night-walk.jpg`

Expected output format:
```
KEY:<challenge key>
FLAG:TDHCTF{exif_shadow_unit}
```

## Step-by-step

### 1) Inspect metadata (fast path)
Use any metadata tool. Example with `exiftool`:
```bash
exiftool -a -u -g1 night-walk.jpg
```

You’re looking for a metadata/comment field that contains a multi-line block including:
- `KEY:<...>`
- `FLAG:TDHCTF{exif_shadow_unit}`
- `UNIT:SHADOW-17` (story flavor)

### 2) If you don’t have exiftool
You can still recover the embedded values by searching printable strings:
```bash
strings -n 6 night-walk.jpg | sed -n '1,200p'
```

You should see lines similar to:
```
KEY:<dynamic key>
FLAG:TDHCTF{exif_shadow_unit}
```

## Author verifier (optional)
From repo root:
```bash
python3 challenges/df-01-night-walk-photo/src/verify_extract.py
```


