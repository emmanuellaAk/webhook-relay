# test_send.py
import hashlib
import hmac
import json

import httpx

from app.config import settings

SECRET = settings.demo_webhook_secret.encode()

body = json.dumps(
    {"id": "evt_005", "type": "payment.succeeded", "amount": 5000}
).encode()

sig = hmac.new(SECRET, body, hashlib.sha256).hexdigest()

r = httpx.post(
    "http://localhost:8000/hooks/demo",
    content=body,
    headers={"Content-Type": "application/json", "X-Webhook-Signature": sig},
)
print(r.status_code, r.text)