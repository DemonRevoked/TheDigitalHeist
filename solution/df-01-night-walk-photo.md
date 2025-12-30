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

### 1) Inspect metadata (find the blob marker)
Use any metadata tool. Example with `exiftool` (recommended):
```bash
exiftool -a -u -g1 night-walk.jpg
```

You’re looking for a comment/metadata block that includes:
- `UNIT:...`
- `CameraModel:...`
- `GPS:...`

And a marker like `--BEGIN-BLOB-B64--` indicating a packed payload is embedded in the comment segment.

### 2) Tool-only extraction (no custom scripts)
The blob is stored in the JPEG **comment**, but you don’t need `exiftool`. Since the blob is base64 text, you can extract it from printable strings and decode it (base64 → gzip):

```bash
cd challenge-files/df-01-night-walk-photo

# 1) Isolate blob + decode (base64 → gzip)
strings -n 8 night-walk.jpg \
  | sed -n '/^--BEGIN-BLOB-B64--$/,/^--END-BLOB-B64--$/p' \
  | sed '1d;$d' \
  | tr -d '\n\r\t ' \
  | base64 -d \
  | gunzip -c
```

Optional (if you have `exiftool` installed), you can extract the comment cleanly first:

```bash
exiftool -b -Comment night-walk.jpg > comment.txt
```

Then run the same `sed`/`tr`/`base64`/`gunzip` pipeline against `comment.txt`.

You should get:
```
KEY:<challenge key>
FLAG:TDHCTF{exif_shadow_unit}
```
