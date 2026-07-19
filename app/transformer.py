import re
from typing import Any

PLACEHOLDER = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def resolve_path(payload: dict, path: str) -> Any:
    """Follow a dotted path like 'data.amount' into a nested dict."""
    value: Any = payload
    for key in path.split("."):
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def render_template(template: Any, payload: dict) -> Any:
    """Recursively fill {{placeholders}} in a template using the payload."""
    if isinstance(template, str):
        match = PLACEHOLDER.fullmatch(template.strip())
        if match:
            return resolve_path(payload, match.group(1))

        def replace(m: re.Match) -> str:
            value = resolve_path(payload, m.group(1))
            return str(value) if value is not None else ""

        return PLACEHOLDER.sub(replace, template)

    if isinstance(template, dict):
        return {key: render_template(val, payload) for key, val in template.items()}

    if isinstance(template, list):
        return [render_template(item, payload) for item in template]

    return template