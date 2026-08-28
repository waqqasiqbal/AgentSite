from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class CapabilityError(ValueError):
    pass


@dataclass(frozen=True)
class Capability:
    """A narrow, typed operation exposed to the model.

    The callable is server-side. Its credentials and raw clients are never placed
    in the model context; only this public contract is sent to the provider.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    execute: Callable[[dict[str, Any], dict[str, Any]], Any]
    risk: str = "read"
    requires_approval: bool = False

    def validate(self, arguments: dict[str, Any]) -> None:
        if not isinstance(arguments, dict):
            raise CapabilityError("arguments must be an object")
        required = self.input_schema.get("required", [])
        missing = [key for key in required if key not in arguments]
        if missing:
            raise CapabilityError(f"missing required arguments: {', '.join(missing)}")
        properties = self.input_schema.get("properties", {})
        for key, value in arguments.items():
            spec = properties.get(key, {})
            expected = spec.get("type")
            if expected == "string" and not isinstance(value, str):
                raise CapabilityError(f"{key} must be a string")
            if expected == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
                raise CapabilityError(f"{key} must be a number")
            if expected == "boolean" and not isinstance(value, bool):
                raise CapabilityError(f"{key} must be a boolean")
            if "enum" in spec and value not in spec["enum"]:
                raise CapabilityError(f"{key} must be one of {spec['enum']}")


class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        if capability.name in self._items:
            raise ValueError(f"capability already registered: {capability.name}")
        self._items[capability.name] = capability

    def get(self, name: str) -> Capability | None:
        return self._items.get(name)

    def definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "description": item.description,
                "input_schema": item.input_schema,
                "risk": item.risk,
                "requires_approval": item.requires_approval,
            }
            for item in self._items.values()
        ]
