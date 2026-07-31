"""Dependency-free HTTP service used to prove ordinary project onboarding."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Final

from reference_app import __version__

SERVICE_NAME: Final = "reference-python"


def response_for(path: str) -> tuple[HTTPStatus, dict[str, str]]:
    """Return the stable semantic response for a request path."""
    if path == "/":
        return HTTPStatus.OK, {
            "service": SERVICE_NAME,
            "version": __version__,
            "message": "infra-k8s reference service",
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
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
