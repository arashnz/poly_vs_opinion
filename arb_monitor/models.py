from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Level:
    price: float
    size: float


@dataclass
class OrderBookSnapshot:
    exchange: str
    market_name: str
    best_bid: Level | None
    best_ask: Level | None
    ts: datetime

    @classmethod
    def empty(cls, exchange: str, market_name: str) -> "OrderBookSnapshot":
        now = datetime.now(timezone.utc)
        return cls(exchange=exchange, market_name=market_name, best_bid=None, best_ask=None, ts=now)


@dataclass
class ArbSignal:
    pair_name: str
    buy_exchange: str
    buy_price: float
    sell_exchange: str
    sell_price: float
    edge: float
    timestamp: datetime

    def key(self) -> str:
        return f"{self.pair_name}:{self.buy_exchange}:{self.sell_exchange}"
