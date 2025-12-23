#!/usr/bin/env sage
"""
The Quantum-Resistant Vault - CRYPTO-03-HARD
Goldwasser-Micali encryption with hint-based RSA factorization
"""

from Crypto.Util.number import getPrime, bytes_to_long
from random import randint
import os
import sys

# Read flag from environment or file
if 'CHALLENGE_FLAG' in os.environ:
    flag = os.environ['CHALLENGE_FLAG'].encode()
elif os.path.exists('/app/flag.txt'):
    with open('/app/flag.txt', 'rb') as f:
        flag = f.read().strip()
else:
    flag = b'TDHCTF{test_flag_hard_crypto}'

print("[+] Generating 1337-bit RSA primes...")
p, q = getPrime(1337), getPrime(1337)
n = p*q

print("[+] Computing hint...")
D = (1*3*3*7)^(1+3+3+7)  # 1337^14
hint = int(D*sqrt(p) + D*sqrt(q))

print("[+] Finding quadratic non-residue...")
x = randint(1337, n)
while 1337:
    lp = legendre_symbol(x, p)
    lq = legendre_symbol(x, q)
    if lp * lq > 0 and lp + lq < 0:
        break
    x = randint(1337, n)

print("[+] Encrypting flag bit-by-bit...")
m = map(int, bin(bytes_to_long(flag))[2:])
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

with open(output_path, 'w') as f:
    f.write('hint = {}\n'.format(hint))
    f.write('D = {}\n'.format(D))
    f.write('n = {}\n'.format(n))
    f.write('c = {}\n'.format(c))

# Save private info for debugging (not accessible to players)
debug_path = '/app/private_key.txt'
with open(debug_path, 'w') as f:
    f.write('p = {}\n'.format(p))
    f.write('q = {}\n'.format(q))
    f.write('x = {}\n'.format(x))
    f.write('flag = {}\n'.format(flag.decode()))

print("[+] Challenge file generated: {}".format(output_path))
print("[+] n = {} bits".format(n.nbits()))
print("[+] Hint = {}".format(hint))
print("[+] D = {}".format(D))
print("[+] Flag encrypted as {} bits".format(len(c)))

