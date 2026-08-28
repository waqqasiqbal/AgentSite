from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from .manifest import AgentManifest
from .models import AgentRequest
from .runtime import AgentRuntime


class AgentSiteHandler(BaseHTTPRequestHandler):
    """Small reference transport. Put authentication in front of this in production."""

    runtime: AgentRuntime
    manifest: AgentManifest
    authenticate: Callable[["AgentSiteHandler", dict[str, Any]], tuple[str, str] | None] | None = None

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/.well-known/agentsite":
            return self._json(200, self.manifest.to_dict())
        if self.path == self.manifest.capabilities_endpoint:
            return self._json(200, {"capabilities": self.runtime.capabilities.definitions()})
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != self.manifest.request_endpoint:
            return self._json(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                return self._json(413, {"error": "request too large"})
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
                return self._json(400, {"error": "text is required"})
            identity = self.authenticate(self, payload) if self.authenticate else None
            if identity is None:
                return self._json(401, {"error": "authentication required"})
            user_id, tenant_id = identity
            response = self.runtime.handle(AgentRequest(payload["text"], user_id, tenant_id))
            return self._json(
                200,
                {
                    "text": response.text,
                    "trace_id": response.trace_id,
                    "results": [
                        {"call_id": r.call_id, "capability": r.capability, "status": r.status, "output": r.output, "error": r.error}
                        for r in response.results
                    ],
                    "pending_approvals": [call.call_id for call in response.pending_approvals],
                },
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "invalid JSON"})
        except Exception:
            self._json(500, {"error": "request processing failed"})

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(runtime: AgentRuntime, manifest: AgentManifest, host: str = "127.0.0.1", port: int = 8080) -> None:
    handler = type("ConfiguredAgentSiteHandler", (AgentSiteHandler,), {"runtime": runtime, "manifest": manifest})
    ThreadingHTTPServer((host, port), handler).serve_forever()
