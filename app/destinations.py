import json
from pathlib import Path

from app.config import settings

TRANSFORMS_DIR = Path(__file__).parent.parent / "transforms"


def load_transform(name: str) -> dict | None:
    path = TRANSFORMS_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


DESTINATIONS: dict[str, dict] = {
    "demo": {
        "url": settings.demo_destination_url,
        "transform": load_transform("demo"),
    },
}