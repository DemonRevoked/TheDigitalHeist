Ghidra Walkthrough (simple steps)
1) Open the file and let Ghidra analyze it

Open Ghidra

File → New Project

Drag the binary into the project (or File → Import File)

Double-click the imported file

When it asks to analyze, click OK (default options)

2) Find the “success” message

Go to Search → For Strings

In the list, find:

"Timeline rewrite validated."

Double-click it

This jumps you to where that text lives in memory.

3) Jump to the code that uses that message

With the string highlighted, press X

(or right-click → References → Show References)

Double-click the reference you see

Now you are inside the function that checks your input.

4) Use the Decompiler view (ignore assembly)

Look at the Decompiler window (it shows C-like code)

Find the line that reads your input number, usually:

strtoull(...)

Find the if (...) check that decides accept/reject.

In your case, the key check is:

uVar11 = (uVar10 ^ 0x5a5a5a5a5a5a5a5a) - 0x1111110a;
if (uVar11 != uVar8) reject;


Write down the constants:

0x5a5a5a5a5a5a5a5a

0x1111110a

5) Find out what uVar8 is

Scroll a little above and you’ll see something like:

FUN_00101900(0x102200, 10, buffer);
uVar8 = strtoull(buffer, 0, 10);


This tells you:

the program decrypts 10 bytes from address 0x102200

then turns them into a number using strtoull

6) Go to that data address and copy the first 10 bytes

Click on 0x102200 in the decompiler

Press G (Go To)

Enter 0x00102200 and press Enter

In the listing view, you’ll see DAT_00102200

Select the first 10 bytes:

e1 90 f6 cd c4 ba 89 92 bf a8

(You already did this correctly.)

7) Understand the trick: strtoull returns 0 if it doesn’t start with digits

Because those decrypted bytes do not become something starting with 0-9,
strtoull(...) becomes:

✅ uVar8 = 0

You can remember this rule:

If decoded text starts with letters, it’s not a number → result 0.

8) Solve the check with uVar8 = 0

You saw the check:

(uVar10 ^ Z) - C == uVar8


With uVar8 = 0:

(uVar10 ^ Z) - C == 0


So:

uVar10 ^ Z = C
uVar10 = C ^ Z


Where:

Z = 0x5a5a5a5a5a5a5a5a

C = 0x1111110a

So:

uVar10 = 0x5a5a5a5a4b4b4b50


Decimal:

✅ 6510615555174255440

9) Enter the answer

Run the program and enter:

6510615555174255440


You should get:

Timeline rewrite validated.