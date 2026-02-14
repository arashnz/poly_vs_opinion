from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class SharedState:
    lock: Lock = field(default_factory=Lock)
    snapshots: dict[str, dict[str, Any]] = field(default_factory=dict)
    signals: list[dict[str, Any]] = field(default_factory=list)
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_snapshot(self, pair_name: str, exchange: str, bid: float | None, ask: float | None) -> None:
        with self.lock:
            bucket = self.snapshots.setdefault(pair_name, {})
            bucket[exchange] = {
                "bid": bid,
                "ask": ask,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            self.last_update = datetime.now(timezone.utc)

    def push_signal(self, signal: dict[str, Any], max_items: int = 100) -> None:
        with self.lock:
            self.signals.insert(0, signal)
            self.signals = self.signals[:max_items]
            self.last_update = datetime.now(timezone.utc)

    def dump(self) -> dict[str, Any]:
        with self.lock:
            return {
                "last_update": self.last_update.isoformat(),
                "snapshots": self.snapshots,
                "signals": self.signals,
            }
