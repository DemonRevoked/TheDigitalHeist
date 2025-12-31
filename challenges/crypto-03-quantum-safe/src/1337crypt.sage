#!/usr/bin/env sage
"""
The Quantum-Resistant Vault - CRYPTO-03-HARD
Goldwasser-Micali encryption with hint-based RSA factorization
"""

from Crypto.Util.number import getPrime, bytes_to_long
from random import randint
import os
import sys

# Read challenge key from environment (flag is constant)
if 'CHALLENGE_KEY' in os.environ:
    challenge_key = os.environ['CHALLENGE_KEY']
else:
    challenge_key = "offline-default-crypto03"

flag = "TDHCTF{quantum_safe_decrypted}"

# Create message containing both key and flag separately
# Format: "KEY: <key>\nFLAG: <flag>"
message = f"KEY: {challenge_key}\nFLAG: {flag}"
message_bytes = message.encode()

print("[+] Generating 1337-bit RSA primes...")
p, q = getPrime(1337), getPrime(1337)
n = p*q

print("[+] Computing hint...")
# IMPORTANT: D must be *huge* so that (hint / D) approximates (sqrt(p) + sqrt(q))
# with enough absolute precision to recover p+q via rounding:
#   p+q = s^2 - 2*sqrt(n), where s ≈ sqrt(p)+sqrt(q)
# With small D this becomes numerically unstable.
D = 1337^100
hint = int(D*sqrt(p) + D*sqrt(q))

print("[+] Finding quadratic non-residue...")
x = randint(1337, n)
while 1337:
    lp = legendre_symbol(x, p)
    lq = legendre_symbol(x, q)
    if lp * lq > 0 and lp + lq < 0:
        break
    x = randint(1337, n)

print("[+] Encrypting message (containing key and flag) bit-by-bit...")
m = map(int, bin(bytes_to_long(message_bytes))[2:])
c = []
for b in m:
    while 1337:
        r = randint(1337, n)
        if gcd(r, n) == 1:
            break
    c.append((pow(x, 1337 + b, n) * pow(r, 1337+1337, n)) % n)

# Write output file
output_path = '/challenge-files/crypto-03-quantum-safe/1337crypt_output.txt'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print("[+] Writing output file to: {}".format(output_path))
with open(output_path, 'w') as f:
    f.write('hint = {}\n'.format(hint))
    f.write('D = {}\n'.format(D))
    f.write('n = {}\n'.format(n))
    f.write('c = {}\n'.format(c))

# Flush and sync to ensure file is written to disk
import sys
sys.stdout.flush()
import os
os.sync()

# Verify file was written
if os.path.exists(output_path):
    file_size = os.path.getsize(output_path)
    print("[+] Output file written successfully, size: {} bytes".format(file_size))
else:
    print("[!] ERROR: Output file was not created!", file=sys.stderr)
    sys.exit(1)

# Save private info for debugging (not accessible to players)
debug_path = '/app/private_key.txt'
with open(debug_path, 'w') as f:
    f.write('p = {}\n'.format(p))
    f.write('q = {}\n'.format(q))
    f.write('x = {}\n'.format(x))
    f.write('challenge_key = {}\n'.format(challenge_key))
    f.write('flag = {}\n'.format(flag))
    f.write('message = {}\n'.format(message))

print("[+] Challenge file generated: {}".format(output_path))
print("[+] n = {} bits".format(n.bit_length()))
print("[+] Hint = {}".format(hint))
print("[+] D = {}".format(D))
print("[+] Message encrypted as {} bits".format(len(c)))
print("[+] Challenge Key: {}".format(challenge_key))
print("[+] Flag: {}".format(flag))

