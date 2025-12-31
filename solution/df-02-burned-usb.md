# df-02-burned-usb — Walkthrough (Burned USB)

## Goal
Recover **both** values from:
- `challenge-files/df-02-burned-usb/burned-usb.img`

Expected output format:
```
KEY:<challenge key>
FLAG:TDHCTF{carved_network_node}
```

## Quick start (copy/paste)

From repo root:

```bash
cd /home/demon/TheDigitalHeist
cd challenge-files/df-02-burned-usb
ls -lh
```

You should see `burned-usb.img`.

## Step-by-step (easy commands + what to expect)

### 1) Confirm the markers exist

The image is a raw blob that contains a **real gzip stream**, but it’s deliberately broken up by **gap blocks**.
First, confirm the gap markers are present:

```bash
grep -a --line-number -m 2 "DIRECTORATE_SCRUB_GAP" burned-usb.img
```

What to expect:
- You should see at least one match. (It may print “Binary file … matches” depending on your grep build — that’s fine.)

### 2) Locate the gzip header and carve from it

We want the gzip header bytes: `1f 8b 08`.

```bash
grep -aob $'\x1f\x8b\x08' burned-usb.img | head -n 5
```

What to expect:
- One or more lines like `12345:<binary...>` (the number before `:` is the byte offset).

If you get multiple hits, pick the one **after** the string `USBIMGv1`:

```bash
grep -aob "USBIMGv1" burned-usb.img | head -n 5
```

What to expect:
- One line like `NNNNN:USBIMGv1` (note the offset). Choose a gzip offset **greater than** this.

Take the correct offset (call it `OFF`), then carve from there:

```bash
OFF=REPLACE_ME
dd if=burned-usb.img of=carved.bin bs=1 skip="$OFF" status=none
ls -lh carved.bin
```

What to expect:
- `carved.bin` should be a non-trivial size (often KBs+). If it’s tiny, you likely picked the wrong offset.

### 3) Remove the “gap blocks” (the deliberate corruption)

The image contains injected blocks delimited by:
- `<<DIRECTORATE_SCRUB_GAP>>`
- `<</DIRECTORATE_SCRUB_GAP>>`

Remove them with a quick Python one-liner (produces a valid gzip file):

```bash
python3 - << 'PY'
import sys
GAP_START=b"<<DIRECTORATE_SCRUB_GAP>>\n"
GAP_END=b"\n<</DIRECTORATE_SCRUB_GAP>>"
data=open("carved.bin","rb").read()
out=bytearray()
i=0
while True:
    j=data.find(GAP_START,i)
    if j==-1:
        out+=data[i:]
        break
    out+=data[i:j]
    k=data.find(GAP_END,j+len(GAP_START))
    if k==-1:
        break
    i=k+len(GAP_END)
open("reassembled.gz","wb").write(bytes(out))
print("wrote reassembled.gz")
PY
```

What to expect:
- It should print `wrote reassembled.gz`.
- `reassembled.gz` should exist and be a reasonable size:

```bash
ls -lh reassembled.gz
file reassembled.gz
```

`file` should say it’s gzip-compressed data.

### 4) Decompress and read the recovered blueprint

```bash
gzip -dc reassembled.gz | sed -n '1,120p'
```

You should see:
- `KEY:<...>`
- `FLAG:TDHCTF{carved_network_node}`
- `NODE:SAFEHOUSE-REGISTRY` (story flavor)

### 5) If gzip fails (common mistake checklist)

If `gzip -dc` errors:
- **Wrong `OFF`**: re-run step 2 and choose a different gzip header offset.
- **Gap markers not fully removed**: re-run step 3 and ensure it creates `reassembled.gz`.

## Author verifier (optional)

From repo root (after you’ve regenerated keys via `startup.sh`):

```bash
cd /home/demon/TheDigitalHeist
python3 challenges/df-02-burned-usb/src/verify_recover.py
```


