"""Canonical Monkeys capability publication for Flask-RESTX OpenAPI tools."""

import re

_HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")


def _text(value, fallback):
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for locale in ("en-US", "zh-CN"):
            localized = value.get(locale)
            if isinstance(localized, str) and localized.strip():
                return localized.strip()
    return fallback


def _ports(declarations, direction, capability_id):
    if declarations is None:
        return []
    if not isinstance(declarations, list):
        raise ValueError(f"Tool {direction} declaration must be an array")
    ports, seen = [], {}
    for index, declaration in enumerate(declarations):
        if not isinstance(declaration, dict):
            raise ValueError(
                f"Tool {direction} declaration at index {index} must be an object"
            )
        name = declaration.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Tool {direction} declaration at index {index} must have a name"
            )
        name = name.strip()
        required, value_type = declaration.get("required", False), declaration.get(
            "type"
        )
        if not isinstance(required, bool):
            raise ValueError(f"Tool {direction} {name} required must be a boolean")
        if value_type is not None and not isinstance(value_type, str):
            raise ValueError(f"Tool {direction} {name} type must be a string")
        signature = (required, value_type)
        if name in seen:
            if seen[name] != signature:
                raise ValueError(
                    f"Tool {direction} {name} has conflicting declarations"
                )
            continue
        seen[name] = signature
        port = {
            "name": name,
            "schemaRef": f"schema://tool/{capability_id}/{direction}/{name}",
            "required": required,
            "multiple": value_type == "array",
        }
        description = declaration.get("description", declaration.get("displayName"))
        if description is not None:
            port["description"] = _text(description, name)
        ports.append(port)
    return ports


def publish_openapi_tool_capability_manifests(
    document, namespace, owner_repo, capability_version="1.0.0"
):
    if not isinstance(document, dict) or not isinstance(document.get("paths"), dict):
        raise ValueError("OpenAPI document paths are required")
    if not isinstance(namespace, str) or not _IDENTIFIER.fullmatch(namespace):
        raise ValueError("Capability namespace is invalid")
    if not isinstance(owner_repo, str) or not owner_repo.strip():
        raise ValueError("Capability owner repository is required")
    for path_item in document["paths"].values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(operation, dict):
                continue
            tool_name = operation.get("x-monkey-tool-name")
            if tool_name is None:
                continue
            if not isinstance(tool_name, str) or not _IDENTIFIER.fullmatch(tool_name):
                raise ValueError("Tool name is invalid")
            capability_id = f"{namespace}_{tool_name}"
            display_name = _text(
                operation.get(
                    "x-monkey-tool-display-name", operation.get("summary")
                ),
                tool_name,
            )
            description = _text(
                operation.get(
                    "x-monkey-tool-description", operation.get("description")
                ),
                display_name,
            )
            operation["x-monkeys-capability-manifest"] = {
                "contract": "CapabilityManifest",
                "id": capability_id,
                "capabilityVersion": operation.get(
                    "x-monkey-tool-version", capability_version
                ),
                "ownerRepo": owner_repo.strip(),
                "kind": "tool",
                "displayName": display_name,
                "description": description,
                "ports": {
                    "inputs": _ports(
                        operation.get("x-monkey-tool-input"), "input", capability_id
                    ),
                    "outputs": _ports(
                        operation.get("x-monkey-tool-output"), "output", capability_id
                    ),
                },
                "runtime": {
                    "providerBindings": [
                        {
                            "providerRef": {"kind": "tool", "id": capability_id},
                            "productContexts": [],
                            "priority": 0,
                        }
                    ],
                    "loading": "on-activation",
                    "stateOwner": "provider",
                    "sideEffects": operation.get(
                        "x-monkey-tool-side-effects", ["network"]
                    ),
                },
                "placement": {
                    "surfaces": ["agent", "workflow"],
                    "slots": [],
                    "variants": [],
                    "tokenRefs": [],
                },
                "accessibility": {
                    "keyboardModel": "tool-form",
                    "focusModel": "host-managed",
                    "labelContract": "tool-display-name",
                },
                "observability": {
                    "eventNamespace": f"tool.{capability_id}",
                    "metrics": ["calls", "duration", "errors"],
                    "evidenceRefs": [],
                },
            }
    return document
