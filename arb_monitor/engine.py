from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .alerts import send_telegram
from .config import MonitorConfig, PairConfig
from .exchanges import OpinionClient, PolymarketClient
from .models import ArbSignal
from .state import SharedState


class MonitorEngine:
    def __init__(self, config: MonitorConfig, state: SharedState) -> None:
        self.config = config
        self.state = state
        self._cooldowns: dict[str, datetime] = {}

    def tick_pair(self, pair: PairConfig) -> None:
        opinion_ob = OpinionClient(pair.opinion, pair.name).fetch_orderbook()
        poly_ob = PolymarketClient(pair.polymarket, pair.name).fetch_orderbook()

        self.state.update_snapshot(pair.name, opinion_ob.exchange, _price(opinion_ob.best_bid), _price(opinion_ob.best_ask))
        self.state.update_snapshot(pair.name, poly_ob.exchange, _price(poly_ob.best_bid), _price(poly_ob.best_ask))

        signals = self._detect(
            pair.name,
            opinion_ob.exchange,
            _price(opinion_ob.best_bid),
            _price(opinion_ob.best_ask),
            poly_ob.exchange,
            _price(poly_ob.best_bid),
            _price(poly_ob.best_ask),
            pair.min_edge,
        )
        for sig in signals:
            self._emit(sig)

    def _detect(
        self,
        pair_name: str,
        ex1: str,
        bid1: float | None,
        ask1: float | None,
        ex2: str,
        bid2: float | None,
        ask2: float | None,
        min_edge: float,
    ) -> list[ArbSignal]:
        now = datetime.now(timezone.utc)
        out: list[ArbSignal] = []
        if bid1 is not None and ask2 is not None and bid1 - ask2 >= min_edge:
            out.append(ArbSignal(pair_name, buy_exchange=ex2, buy_price=ask2, sell_exchange=ex1, sell_price=bid1, edge=bid1 - ask2, timestamp=now))
        if bid2 is not None and ask1 is not None and bid2 - ask1 >= min_edge:
            out.append(ArbSignal(pair_name, buy_exchange=ex1, buy_price=ask1, sell_exchange=ex2, sell_price=bid2, edge=bid2 - ask1, timestamp=now))
        return out

    def _emit(self, signal: ArbSignal) -> None:
        key = signal.key()
        now = datetime.now(timezone.utc)
        last = self._cooldowns.get(key)
        if last and now - last < timedelta(seconds=self.config.cooldown_seconds):
            return

        message = (
            f"BOOM 💥 ARB: {signal.pair_name}\n"
            f"Buy {signal.buy_exchange} @ {signal.buy_price:.4f}\n"
            f"Sell {signal.sell_exchange} @ {signal.sell_price:.4f}\n"
            f"Edge: {signal.edge:.4f}"
        )
        send_telegram(self.config.telegram.bot_token, self.config.telegram.chat_id, message)
        self.state.push_signal(
            {
                "pair": signal.pair_name,
                "buy_exchange": signal.buy_exchange,
                "buy_price": signal.buy_price,
                "sell_exchange": signal.sell_exchange,
                "sell_price": signal.sell_price,
                "edge": signal.edge,
                "ts": signal.timestamp.isoformat(),
                "message": message,
            }
        )
        self._cooldowns[key] = now


def _price(level) -> float | None:
    return None if level is None else level.price
