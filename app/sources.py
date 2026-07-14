import hashlib
import hmac

from fastapi import HTTPException, Request

from app.config import settings


def verify_generic_hmac(request: Request, raw_body: bytes, secret: str) -> None:
    """Caller sends hex HMAC-SHA256 of the raw body in X-Webhook-Signature."""
    received_sig = request.headers.get("X-Webhook-Signature")
    if not received_sig:
        raise HTTPException(status_code=401, detail="Missing signature header")

    expected_sig = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(received_sig, expected_sig):
        raise HTTPException(status_code=401, detail="Invalid signature")


SOURCES: dict[str, dict] = {
    "demo": {
        "secret": settings.demo_webhook_secret,
        "verify": verify_generic_hmac,
        "event_id_path": ("body", "id"),
        "event_type_path": ("body", "type"),
    },
}