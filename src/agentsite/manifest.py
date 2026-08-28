from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AgentManifest:
    """Public discovery metadata; never include secrets or internal URLs here."""

    name: str
    display_name: str
    description: str
    protocol_version: str = "0.1"
    request_endpoint: str = "/v1/requests"
    capabilities_endpoint: str = "/.well-known/agentsite/capabilities"
    authentication: tuple[str, ...] = ("bearer",)
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "protocol_version": self.protocol_version,
            "request_endpoint": self.request_endpoint,
            "capabilities_endpoint": self.capabilities_endpoint,
            "authentication": list(self.authentication),
            "capabilities": list(self.capabilities),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AgentManifest":
        required = ("name", "display_name", "description")
        missing = [key for key in required if not raw.get(key)]
        if missing:
            raise ValueError(f"manifest missing required fields: {', '.join(missing)}")
        name = raw["name"]
        if not isinstance(name, str) or "/" in name or " " in name:
            raise ValueError("manifest name must be a compact identifier")
        capabilities = raw.get("capabilities", [])
        if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
            raise ValueError("manifest capabilities must be a list of strings")
        return cls(
            name=name,
            display_name=raw["display_name"],
            description=raw["description"],
            protocol_version=raw.get("protocol_version", "0.1"),
            request_endpoint=raw.get("request_endpoint", "/v1/requests"),
            capabilities_endpoint=raw.get("capabilities_endpoint", "/.well-known/agentsite/capabilities"),
            authentication=tuple(raw.get("authentication", ["bearer"])),
            capabilities=tuple(capabilities),
            metadata=raw.get("metadata", {}),
        )


def load_manifest(path: str | Path) -> AgentManifest:
    with Path(path).open(encoding="utf-8") as handle:
        return AgentManifest.from_dict(json.load(handle))
