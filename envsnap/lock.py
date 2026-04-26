"""Lock/unlock snapshots to prevent accidental modification or deletion."""

from __future__ import annotations

from typing import Any


class LockError(Exception):
    """Raised when a lock-related operation fails."""


def lock_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a new snapshot dict with locked=True."""
    if not isinstance(snapshot, dict):
        raise LockError("snapshot must be a dict")
    return {**snapshot, "locked": True}


def unlock_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a new snapshot dict with locked removed (or False)."""
    if not isinstance(snapshot, dict):
        raise LockError("snapshot must be a dict")
    updated = {**snapshot}
    updated.pop("locked", None)
    return updated


def is_locked(snapshot: dict[str, Any]) -> bool:
    """Return True if the snapshot is locked."""
    return bool(snapshot.get("locked", False))


def assert_unlocked(snapshot: dict[str, Any], operation: str = "modify") -> None:
    """Raise LockError if snapshot is locked."""
    if is_locked(snapshot):
        name = snapshot.get("name", "<unknown>")
        raise LockError(
            f"Cannot {operation} snapshot '{name}': it is locked. "
            "Use 'unlock' first."
        )
