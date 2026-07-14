# worker.py
import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select

from app.db import SessionLocal
from app.destinations import DESTINATIONS
from app.models import Event, EventStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("worker")

POLL_INTERVAL = 2          # seconds between checks of the notebook
BATCH_SIZE = 10            # max events claimed per cycle
MAX_ATTEMPTS = 5
BACKOFF_SCHEDULE = [30, 120, 600, 3600]   # seconds: 30s, 2min, 10min, 1hr


def next_retry_delay(attempts: int) -> int:
    index = min(attempts - 1, len(BACKOFF_SCHEDULE) - 1)
    return BACKOFF_SCHEDULE[index]


async def claim_events(session) -> list[Event]:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(Event)
        .where(
            Event.status == EventStatus.pending,
            (Event.next_retry_at.is_(None)) | (Event.next_retry_at <= now),
        )
        .order_by(Event.received_at)
        .limit(BATCH_SIZE)
        .with_for_update(skip_locked=True)
    )
    events = list(result.scalars())
    for event in events:
        event.status = EventStatus.delivering
    await session.commit()
    return events


async def deliver(client: httpx.AsyncClient, event: Event) -> None:
    url = DESTINATIONS.get(event.source)
    if url is None:
        raise RuntimeError(f"No destination configured for source {event.source!r}")

    response = await client.post(url, json=event.payload, timeout=10.0)
    response.raise_for_status()


async def process_event(client: httpx.AsyncClient, event_id: int) -> None:
    async with SessionLocal() as session:
        event = await session.get(Event, event_id)

        try:
            await deliver(client, event)
        except Exception as exc:
            event.attempts += 1
            event.last_error = str(exc)[:500]
            if event.attempts >= MAX_ATTEMPTS:
                event.status = EventStatus.failed
                log.warning("event %s FAILED permanently: %s", event.id, exc)
            else:
                delay = next_retry_delay(event.attempts)
                event.status = EventStatus.pending
                event.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                log.info("event %s failed (attempt %s), retry in %ss", event.id, event.attempts, delay)
        else:
            event.status = EventStatus.delivered
            event.delivered_at = datetime.now(timezone.utc)
            log.info("event %s delivered", event.id)

        await session.commit()


async def main() -> None:
    log.info("worker starting, polling every %ss", POLL_INTERVAL)
    async with httpx.AsyncClient() as client:
        while True:
            async with SessionLocal() as session:
                events = await claim_events(session)

            for event in events:
                await process_event(client, event.id)

            if not events:
                await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())