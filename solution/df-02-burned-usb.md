# df-02-burned-usb — Walkthrough (Burned USB)

## Goal
Recover **both** values from:
- `challenge-files/df-02-burned-usb/burned-usb.img`

Expected output format:
```
KEY:<challenge key>
FLAG:TDHCTF{carved_network_node}
```

## Step-by-step

### 1) Find the embedded gzip stream
Search for a gzip header (`1f 8b 08`) inside the image:
```bash
grep -aob $'\x1f\x8b\x08' burned-usb.img | head
```

If you get multiple hits (false positives can happen in random bytes), prefer the gzip header **after**
the marker string `USBIMGv1`.

Take the correct offset (call it `OFF`), then carve from there:
```bash
dd if=burned-usb.img of=carved.bin bs=1 skip=OFF status=none
```

### 2) Remove the “gap blocks” (the deliberate corruption)
The image contains injected blocks delimited by:
- `<<DIRECTORATE_SCRUB_GAP>>`
- `<</DIRECTORATE_SCRUB_GAP>>`

Remove them with a quick Python one-liner:
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

### 3) Decompress and read the recovered blueprint
```bash
gzip -dc reassembled.gz | sed -n '1,120p'
```

You should see:
- `KEY:<...>`
- `FLAG:TDHCTF{carved_network_node}`
- `NODE:SAFEHOUSE-REGISTRY` (story flavor)

## Author verifier (optional)
From repo root:
```bash
python3 challenges/df-02-burned-usb/src/verify_recover.py
```


