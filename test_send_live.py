import hashlib
import hmac
import json
import httpx

URL = "https://relay-api-p2pp.onrender.com/hooks/demo"
SECRET = b"fb68f3d76fc4c6c1812bba50ff260095ff839c64a6675e978e58413dd33bf168"

body = json.dumps({"id": "evt_live_1", "type": "payment.succeeded", "amount": 5000}).encode()
sig = hmac.new(SECRET, body, hashlib.sha256).hexdigest()

r = httpx.post(
    URL,
    content=body,
    headers={"Content-Type": "application/json", "X-Webhook-Signature": sig},
)
print(r.status_code, r.text)
