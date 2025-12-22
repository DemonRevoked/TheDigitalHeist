## Challenge 2 — `FUN_001010a0`

### Evidence Tampering Console

### Objective

Determine the correct **epoch timestamp** that passes validation.

---

## Step 1: Understand Input Validation

User input is read and parsed as a 64-bit integer:

```c
uVar4 = strtoull(local_a8, &endptr, 10);
```

Then validated using:

```c
if ((uVar4 ^ 0x5a5a5a5a5a5a5a5a) - 0x1111110a == uVar5)
```

We must determine `uVar5`.

---

## Step 2: Recover the Hidden Target Value

The function builds a hidden decimal string:

```c
local_bd[10+i] = local_bd[i] ^ 0x2a;
uVar5 = strtoull((char *)(local_bd + 10), 0, 10);
```

XOR-decoding produces:

```text
1700013377
```

So:

```text
uVar5 = 1700013377
```

---

## Step 3: Solve the Validation Equation

Given:

```text
(uVar4 ^ K) - C = uVar5
```

Where:

* `K = 0x5a5a5a5a5a5a5a5a`
* `C = 0x1111110a`
* `uVar5 = 1700013377`

Rearrange:

```text
uVar4 = (uVar5 + C) ^ K
```

---

## Step 4: Compute the Required Input

```text
1700013377 + 0x1111110a = 1986344523
1986344523 ^ 0x5a5a5a5a5a5a5a5a = 6510615554653383697
```

---

## Step 5: Solution Summary

**Input to provide**

```text
6510615554653383697
```

**Flag obtained**

```text
TDHCTF{tampered_time_offset}
```

---
