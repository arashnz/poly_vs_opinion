from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable


class Handler(BaseHTTPRequestHandler):
    state_getter: Callable[[], dict] | None = None

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/state":
            data = json.dumps(self.state_getter() if self.state_getter else {}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if self.path in {"/", "/index.html"}:
            html = Path("templates/index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, _fmt: str, *_args) -> None:
        return


def start_dashboard(port: int, state_getter: Callable[[], dict]) -> ThreadingHTTPServer:
    Handler.state_getter = state_getter
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    return server
