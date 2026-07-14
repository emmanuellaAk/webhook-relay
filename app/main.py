import json

from fastapi import FastAPI, HTTPException, Request
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import Event
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