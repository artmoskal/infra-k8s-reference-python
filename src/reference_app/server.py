"""Dependency-free HTTP service used to prove ordinary project onboarding."""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Final

from reference_app import __version__

SERVICE_NAME: Final = "reference-python"
SOURCE_ROOT: Final = Path(__file__).resolve().parent
MESSAGE_FILE: Final = Path("/app/config/message.json")


def configured_message() -> str:
    """Read the ordinary project-owned config synchronized in dev mode."""
    try:
        value = json.loads(MESSAGE_FILE.read_text()).get("message")
    except (OSError, ValueError, AttributeError):
        return "infra-k8s reference service"
    return value if isinstance(value, str) and value else "infra-k8s reference service"


def response_for(path: str) -> tuple[HTTPStatus, dict[str, str]]:
    """Return the stable semantic response for a request path."""
    if path == "/":
        return HTTPStatus.OK, {
            "service": SERVICE_NAME,
            "version": __version__,
            "message": configured_message(),
        }
    if path == "/health":
        return HTTPStatus.OK, {"service": SERVICE_NAME, "status": "ok"}
    return HTTPStatus.NOT_FOUND, {"service": SERVICE_NAME, "status": "not-found"}


class Handler(BaseHTTPRequestHandler):
    """Serve only the reference API; access logging stays with the runtime."""

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        status, payload = response_for(self.path.split("?", 1)[0])
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    threading.Thread(target=reload_when_source_changes, daemon=True).start()
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


def reload_when_source_changes() -> None:
    """Re-exec after the bounded dev sync updates source in the running image."""
    baseline = source_signature()
    while True:
        time.sleep(0.25)
        current = source_signature()
        if current != baseline:
            os.execv(sys.executable, [sys.executable, "-m", "reference_app.server"])


def source_signature() -> tuple[tuple[str, int, int], ...]:
    return tuple(
        (str(path), path.stat().st_mtime_ns, path.stat().st_size)
        for path in sorted(SOURCE_ROOT.glob("*.py"))
    )


if __name__ == "__main__":
    main()
