import json

from fastapi import FastAPI, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models import Event, EventStatus
from app.db import SessionLocal
from app.sources import SOURCES

app = FastAPI(title="Webhook Relay")


def extract(payload: dict, request: Request, path: tuple[str, str]) -> str:
    location, key = path
    if location == "header":
        value = request.headers.get(key)
    else:
        value = payload.get(key)
    if not value:
        raise HTTPException(status_code=422, detail=f"Missing {key}")
    return str(value)


@app.post("/hooks/{source_name}", status_code=200)
async def ingest(source_name: str, request: Request):
    source = SOURCES.get(source_name)
    if source is None:
        raise HTTPException(status_code=404, detail="Unknown source")

    raw_body = await request.body()

    source["verify"](request, raw_body, source["secret"])

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Body is not valid JSON")

    event = Event(
        source=source_name,
        external_id=extract(payload, request, source["event_id_path"]),
        event_type=extract(payload, request, source["event_type_path"]),
        payload=payload,
    )

    async with SessionLocal() as session:
        session.add(event)
        try:
            await session.commit()
        except IntegrityError:
            return {"status": "duplicate", "detail": "Event already received"}

    return {"status": "accepted", "id": event.id}

@app.get("/events")
async def list_events(status: str | None = None, limit: int = 50):
    async with SessionLocal() as session:
        query = select(Event).order_by(Event.received_at.desc()).limit(limit)
        if status is not None:
            query = query.where(Event.status == status)
        result = await session.execute(query)
        events = result.scalars().all()

        return [
            {
                "id": e.id,
                "source": e.source,
                "external_id": e.external_id,
                "event_type": e.event_type,
                "status": e.status,
                "attempts": e.attempts,
                "last_error": e.last_error,
                "received_at": e.received_at.isoformat(),
            }
            for e in events
        ]
    
@app.post("/events/{event_id}/replay")
async def replay_event(event_id: int):
    async with SessionLocal() as session:
        event = await session.get(Event, event_id)

        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != EventStatus.failed:
            raise HTTPException(
                status_code=409,
                detail=f"Only failed events can be replayed (this one is {event.status.value})",
            )

        event.status = EventStatus.pending
        event.attempts = 0
        event.next_retry_at = None
        event.last_error = None
        await session.commit()

        return {"status": "replaying", "id": event.id}