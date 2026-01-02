import base64, json, hmac, hashlib, time
from django.conf import settings

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("utf-8"))

def sign_token(payload: dict) -> str:
    # Very small JWT-like token: header.payload.signature (HMAC-SHA256)
    header = {"alg":"HS256","typ":"QR"}
    header_b = _b64url(json.dumps(header, separators=(",",":")).encode("utf-8"))
    payload_b = _b64url(json.dumps(payload, separators=(",",":")).encode("utf-8"))
    msg = f"{header_b}.{payload_b}".encode("utf-8")
    sig = hmac.new(settings.QR_SIGNING_KEY.encode("utf-8"), msg, hashlib.sha256).digest()
    sig_b = _b64url(sig)
    return f"{header_b}.{payload_b}.{sig_b}"

def verify_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Token inválido")
    header_b, payload_b, sig_b = parts
    msg = f"{header_b}.{payload_b}".encode("utf-8")
    expected = hmac.new(settings.QR_SIGNING_KEY.encode("utf-8"), msg, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64url_decode(sig_b)):
        raise ValueError("Firma inválida")
    payload = json.loads(_b64url_decode(payload_b))
    exp = payload.get("exp")
    if exp and int(time.time()) > int(exp):
        raise ValueError("QR vencido")
    return payload
