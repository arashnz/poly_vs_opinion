from datetime import timezone

from arb_monitor.config import MonitorConfig, TelegramConfig
from arb_monitor.engine import MonitorEngine
from arb_monitor.state import SharedState


def make_cfg() -> MonitorConfig:
    return MonitorConfig(
        poll_interval_seconds=1,
        cooldown_seconds=30,
        dashboard_port=8080,
        telegram=TelegramConfig(bot_token="x", chat_id="y"),
        pairs=[],
    )


def test_detect_two_way_signal():
    engine = MonitorEngine(make_cfg(), SharedState())
    signals = engine._detect("m", "A", 0.58, 0.49, "B", 0.52, 0.45, 0.01)
    assert len(signals) == 2
    assert signals[0].timestamp.tzinfo == timezone.utc


def test_detect_no_signal_when_missing_levels():
    engine = MonitorEngine(make_cfg(), SharedState())
    signals = engine._detect("m", "A", None, 0.60, "B", 0.52, None, 0.01)
    assert signals == []
