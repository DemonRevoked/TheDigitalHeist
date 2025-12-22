Find the call site

Open the main check function.

Locate: FUN_00101a00(0x102160, 0x32, ...)

This tells you: address = 0x102160, length = 0x32 (50).

Extract the bytes

Press G → go to 0x00102160

In the Listing, select 50 bytes from 00102160 through 00102191

Right-click → Copy Special → Byte String (or copy as hex)

Decode them

Use the XOR formula from FUN_00101a00 (above) in a tiny script (or a Ghidra script).

The output you should get is:

su ot delaever won si noitacol yawetag krowten eTh

Reverse the decoded output

Because the program reverses your input before comparing.

The reversed string is the passphrase:

hTe network gateway location is now revealed to us

If you want, paste the bytes for DAT_00102192 or DAT_001021ae too and I’ll decode those strings as well (they’re likely the prompt / success messages).