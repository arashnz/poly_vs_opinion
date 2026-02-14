from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TelegramConfig:
    bot_token: str
    chat_id: str


@dataclass
class OpinionConfig:
    base_url: str = "https://api.opinion.trade"
    orderbook_path: str = "/v1/orderbook"
    topic_id: int = 0
    outcome_id: str = ""
    api_key: str = ""


@dataclass
class PolymarketConfig:
    clob_base_url: str = "https://clob.polymarket.com"
    book_path: str = "/book"
    token_id: str = ""
    ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    use_ws: bool = False


@dataclass
class PairConfig:
    name: str
    min_edge: float
    opinion: OpinionConfig
    polymarket: PolymarketConfig


@dataclass
class MonitorConfig:
    poll_interval_seconds: float
    cooldown_seconds: int
    dashboard_port: int
    telegram: TelegramConfig
    pairs: list[PairConfig] = field(default_factory=list)


def _env_expand(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        return os.getenv(value[2:-1], "")
    if isinstance(value, dict):
        return {k: _env_expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_env_expand(v) for v in value]
    return value


def load_config(path: str | Path) -> MonitorConfig:
    raw = _env_expand(json.loads(Path(path).read_text()))

    telegram = TelegramConfig(
        bot_token=str(raw["telegram"]["bot_token"]),
        chat_id=str(raw["telegram"]["chat_id"]),
    )

    pairs: list[PairConfig] = []
    for p in raw.get("pairs", []):
        opinion = OpinionConfig(
            base_url=p["opinion"].get("base_url", "https://api.opinion.trade"),
            orderbook_path=p["opinion"].get("orderbook_path", "/v1/orderbook"),
            topic_id=int(p["opinion"]["topic_id"]),
            outcome_id=str(p["opinion"]["outcome_id"]),
            api_key=str(p["opinion"].get("api_key", "")),
        )
        poly = PolymarketConfig(
            clob_base_url=p["polymarket"].get("clob_base_url", "https://clob.polymarket.com"),
            book_path=p["polymarket"].get("book_path", "/book"),
            token_id=str(p["polymarket"]["token_id"]),
            ws_url=p["polymarket"].get("ws_url", "wss://ws-subscriptions-clob.polymarket.com/ws/market"),
            use_ws=bool(p["polymarket"].get("use_ws", False)),
        )
        pairs.append(PairConfig(name=p["name"], min_edge=float(p.get("min_edge", raw.get("min_edge", 0.01))), opinion=opinion, polymarket=poly))

    return MonitorConfig(
        poll_interval_seconds=float(raw.get("poll_interval_seconds", 2.0)),
        cooldown_seconds=int(raw.get("cooldown_seconds", 30)),
        dashboard_port=int(raw.get("dashboard", {}).get("port", 8080)),
        telegram=telegram,
        pairs=pairs,
    )
