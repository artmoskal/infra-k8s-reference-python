import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from reference_app import server as reference_server  # noqa: E402
from reference_app.server import Handler, response_for  # noqa: E402


class ResponseTest(unittest.TestCase):
    def test_semantic_responses(self) -> None:
        self.assertEqual(
            response_for("/health"),
            (HTTPStatus.OK, {"service": "reference-python", "status": "ok"}),
        )
        status, root = response_for("/")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(root["service"], "reference-python")
        self.assertEqual(root["version"], "1.0.0")

    def test_unknown_path_is_not_a_false_health_success(self) -> None:
        self.assertEqual(response_for("/missing")[0], HTTPStatus.NOT_FOUND)

    def test_project_owned_json_config_changes_the_live_response(self) -> None:
        original = reference_server.MESSAGE_FILE
        with tempfile.TemporaryDirectory() as directory:
            fixture = os.path.join(directory, "message.json")
            with open(fixture, "w", encoding="utf-8") as output:
                json.dump({"message": "changed-by-consumer"}, output)
            reference_server.MESSAGE_FILE = reference_server.Path(fixture)
            try:
                self.assertEqual(response_for("/")[1]["message"], "changed-by-consumer")
            finally:
                reference_server.MESSAGE_FILE = original


class HTTPTest(unittest.TestCase):
    def test_real_http_handler(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{server.server_port}/health", timeout=2
            ) as response:
                self.assertEqual(response.status, HTTPStatus.OK)
                self.assertEqual(response.headers["Content-Type"], "application/json")
                self.assertEqual(
                    json.load(response),
                    {"service": "reference-python", "status": "ok"},
                )
            with self.assertRaises(urllib.error.HTTPError) as missing:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{server.server_port}/missing", timeout=2
                )
            self.assertEqual(missing.exception.code, HTTPStatus.NOT_FOUND)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
