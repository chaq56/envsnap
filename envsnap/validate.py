"""Validation utilities for envsnap snapshots."""

from __future__ import annotations

from typing import Any

REQUIRED_SNAPSHOT_KEYS = {"name", "timestamp", "env"}


class SnapshotValidationError(Exception):
    """Raised when a snapshot fails validation."""


def validate_snapshot(snapshot: Any) -> None:
    """Validate that a snapshot dict has the expected structure.

    Args:
        snapshot: The object to validate.

    Raises:
        SnapshotValidationError: If the snapshot is invalid.
    """
    if not isinstance(snapshot, dict):
        raise SnapshotValidationError(
            f"Snapshot must be a dict, got {type(snapshot).__name__}"
        )

    missing = REQUIRED_SNAPSHOT_KEYS - snapshot.keys()
    if missing:
        raise SnapshotValidationError(
            f"Snapshot is missing required keys: {sorted(missing)}"
        )

    if not isinstance(snapshot["name"], str) or not snapshot["name"].strip():
        raise SnapshotValidationError(
            "Snapshot 'name' must be a non-empty string."
        )

    if not isinstance(snapshot["timestamp"], str) or not snapshot["timestamp"].strip():
        raise SnapshotValidationError(
            "Snapshot 'timestamp' must be a non-empty string."
        )

    if not isinstance(snapshot["env"], dict):
        raise SnapshotValidationError(
            f"Snapshot 'env' must be a dict, got {type(snapshot['env']).__name__}"
        )

    for key, value in snapshot["env"].items():
        if not isinstance(key, str):
            raise SnapshotValidationError(
                f"All env keys must be strings; got key {key!r} of type {type(key).__name__}"
            )
        if not isinstance(value, str):
            raise SnapshotValidationError(
                f"All env values must be strings; key {key!r} has value of type {type(value).__name__}"
            )


def is_valid_snapshot(snapshot: Any) -> bool:
    """Return True if the snapshot passes validation, False otherwise."""
    try:
        validate_snapshot(snapshot)
        return True
    except SnapshotValidationError:
        return False
