"""Pin specific environment variable keys in a snapshot to prevent them from being overwritten during merge or restore."""

from __future__ import annotations

from typing import Any

PINNED_KEY = "pinned_keys"


class PinError(Exception):
    """Raised when a pin operation fails."""


def pin_keys(snapshot: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """Return a new snapshot with the given keys added to the pinned list."""
    if not isinstance(snapshot, dict):
        raise PinError("snapshot must be a dict")
    env = snapshot.get("env", {})
    missing = [k for k in keys if k not in env]
    if missing:
        raise PinError(f"Keys not found in snapshot env: {missing}")
    existing = set(snapshot.get(PINNED_KEY, []))
    updated = sorted(existing | set(keys))
    return {**snapshot, PINNED_KEY: updated}


def unpin_keys(snapshot: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """Return a new snapshot with the given keys removed from the pinned list."""
    if not isinstance(snapshot, dict):
        raise PinError("snapshot must be a dict")
    existing = set(snapshot.get(PINNED_KEY, []))
    not_pinned = [k for k in keys if k not in existing]
    if not_pinned:
        raise PinError(f"Keys are not currently pinned: {not_pinned}")
    updated = sorted(existing - set(keys))
    return {**snapshot, PINNED_KEY: updated}


def list_pinned(snapshot: dict[str, Any]) -> list[str]:
    """Return the list of pinned keys for a snapshot."""
    if not isinstance(snapshot, dict):
        raise PinError("snapshot must be a dict")
    return list(snapshot.get(PINNED_KEY, []))


def is_pinned(snapshot: dict[str, Any], key: str) -> bool:
    """Return True if the given key is pinned in the snapshot."""
    return key in snapshot.get(PINNED_KEY, [])


def filter_unpinned(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return only the env entries whose keys are NOT pinned."""
    if not isinstance(snapshot, dict):
        raise PinError("snapshot must be a dict")
    pinned = set(snapshot.get(PINNED_KEY, []))
    filtered_env = {k: v for k, v in snapshot.get("env", {}).items() if k not in pinned}
    return {**snapshot, "env": filtered_env}
