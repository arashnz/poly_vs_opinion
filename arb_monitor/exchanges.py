from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .config import OpinionConfig, PolymarketConfig
from .http import get_json, make_url
from .models import Level, OrderBookSnapshot


@dataclass
class TopOfBook:
    bid: Level | None
    ask: Level | None


class OpinionClient:
    """Opinion API client (no HTML scraping)."""

    def __init__(self, cfg: OpinionConfig, market_name: str) -> None:
        self.cfg = cfg
        self.market_name = market_name

    def fetch_orderbook(self) -> OrderBookSnapshot:
        params = {"topicId": self.cfg.topic_id, "outcomeId": self.cfg.outcome_id}
        url = make_url(self.cfg.base_url, self.cfg.orderbook_path, params)
        headers = {"Accept": "application/json"}
        if self.cfg.api_key:
            headers["Authorization"] = f"Bearer {self.cfg.api_key}"

        payload = get_json(url, headers=headers)
        top = self._parse(payload)
        return OrderBookSnapshot(
            exchange="Opinion",
            market_name=self.market_name,
            best_bid=top.bid,
            best_ask=top.ask,
            ts=datetime.now(timezone.utc),
        )

    @staticmethod
    def _parse(payload: Any) -> TopOfBook:
        root = payload.get("data", payload) if isinstance(payload, dict) else {}
        bids = root.get("bids", []) if isinstance(root, dict) else []
        asks = root.get("asks", []) if isinstance(root, dict) else []
        return TopOfBook(_best_bid(bids), _best_ask(asks))


class PolymarketClient:
    """Polymarket CLOB client. REST is primary; WS flag is for future incremental updates."""

    def __init__(self, cfg: PolymarketConfig, market_name: str) -> None:
        self.cfg = cfg
        self.market_name = market_name

    def fetch_orderbook(self) -> OrderBookSnapshot:
        # Official CLOB REST book endpoint
        url = make_url(self.cfg.clob_base_url, self.cfg.book_path, {"token_id": self.cfg.token_id})
        payload = get_json(url, headers={"Accept": "application/json"})
        top = self._parse(payload)
        return OrderBookSnapshot(
            exchange="Polymarket",
            market_name=self.market_name,
            best_bid=top.bid,
            best_ask=top.ask,
            ts=datetime.now(timezone.utc),
        )

    @staticmethod
    def _parse(payload: Any) -> TopOfBook:
        bids = payload.get("bids", []) if isinstance(payload, dict) else []
        asks = payload.get("asks", []) if isinstance(payload, dict) else []
        return TopOfBook(_best_bid(bids), _best_ask(asks))


def _to_level(item: Any) -> Level | None:
    if isinstance(item, dict):
        price = item.get("price")
        size = item.get("size", item.get("amount", 0))
    elif isinstance(item, (list, tuple)) and len(item) >= 2:
        price, size = item[0], item[1]
    else:
        return None
    try:
        return Level(float(price), float(size))
    except (TypeError, ValueError):
        return None


def _best_bid(bids: list[Any]) -> Level | None:
    parsed = [lvl for lvl in (_to_level(i) for i in bids) if lvl is not None]
    return max(parsed, key=lambda l: l.price) if parsed else None


def _best_ask(asks: list[Any]) -> Level | None:
    parsed = [lvl for lvl in (_to_level(i) for i in asks) if lvl is not None]
    return min(parsed, key=lambda l: l.price) if parsed else None
