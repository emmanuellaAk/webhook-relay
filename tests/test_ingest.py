import hashlib
import hmac
import json

import pytest
import psycopg2

from app.config import settings

SECRET = settings.demo_webhook_secret.encode()
TEST_DB_DSN = "dbname=relay_test user=relay password=relay host=localhost port=5433"


def sign(body: bytes) -> str:
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_valid_webhook_is_accepted(client):
    body = json.dumps({"id": "evt_test_1", "type": "payment.succeeded"}).encode()
    resp = await client.post(
        "/hooks/demo", content=body,
        headers={"X-Webhook-Signature": sign(body)},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_tampered_payload_is_rejected(client):
    body = json.dumps({"id": "evt_test_2", "type": "payment.succeeded"}).encode()
    good_sig = sign(body)
    tampered = body.replace(b"evt_test_2", b"evt_HACKED")
    resp = await client.post(
        "/hooks/demo", content=tampered,
        headers={"X-Webhook-Signature": good_sig},
    )
    assert resp.status_code == 401


def test_duplicate_is_rejected_by_constraint(client):
    """The unique constraint on (source, external_id) enforces dedupe at the DB level."""
    conn = psycopg2.connect(TEST_DB_DSN)
    conn.autocommit = True
    cur = conn.cursor()

    insert = (
        "INSERT INTO events (source, external_id, event_type, payload, status, attempts) "
        "VALUES ('demo', 'evt_dup', 'payment.succeeded', '{}', 'pending', 0)"
    )
    cur.execute(insert)  # first insert succeeds

    with pytest.raises(psycopg2.errors.UniqueViolation):
        cur.execute(insert)  # second insert violates the unique constraint

    cur.close()
    conn.close()
