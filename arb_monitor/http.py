from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


def get_json(url: str, headers: dict[str, str] | None = None, timeout: float = 10.0) -> Any:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def make_url(base_url: str, endpoint: str, params: dict[str, Any]) -> str:
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None and v != ""})
    path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    base = f"{base_url.rstrip('/')}{path}"
    return f"{base}?{query}" if query else base
