from __future__ import annotations

import argparse
import threading
import time
import traceback

from .config import load_config
from .dashboard import start_dashboard
from .engine import MonitorEngine
from .state import SharedState


def run() -> None:
    parser = argparse.ArgumentParser(description="Opinion vs Polymarket arb monitor")
    parser.add_argument("--config", default="config.json", help="Path to JSON config")
    args = parser.parse_args()

    config = load_config(args.config)
    state = SharedState()
    engine = MonitorEngine(config, state)

    server = start_dashboard(config.dashboard_port, state.dump)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"Dashboard running at http://127.0.0.1:{config.dashboard_port}")

    while True:
        for pair in config.pairs:
            try:
                engine.tick_pair(pair)
            except Exception as exc:  # noqa: BLE001
                print(f"tick failed for {pair.name}: {exc}")
                traceback.print_exc()
            time.sleep(config.poll_interval_seconds)


if __name__ == "__main__":
    run()
