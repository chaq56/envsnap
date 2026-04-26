"""Track snapshot access and modification history."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

HISTORY_FILENAME = ".history.json"
MAX_HISTORY_ENTRIES = 200


def _history_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / HISTORY_FILENAME


def _load_history(snapshot_dir: str) -> List[dict]:
    path = _history_path(snapshot_dir)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_history(snapshot_dir: str, entries: List[dict]) -> None:
    path = _history_path(snapshot_dir)
    Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
    trimmed = entries[-MAX_HISTORY_ENTRIES:]
    with path.open("w", encoding="utf-8") as fh:
        json.dump(trimmed, fh, indent=2)


def record_event(
    snapshot_dir: str,
    action: str,
    snapshot_name: str,
    detail: Optional[str] = None,
) -> dict:
    """Append an event to the history log and return the new entry."""
    if action not in {"capture", "load", "delete", "restore", "export", "merge", "tag"}:
        raise ValueError(f"Unknown action: {action!r}")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "snapshot": snapshot_name,
    }
    if detail:
        entry["detail"] = detail
    entries = _load_history(snapshot_dir)
    entries.append(entry)
    _save_history(snapshot_dir, entries)
    return entry


def get_history(
    snapshot_dir: str,
    snapshot_name: Optional[str] = None,
    action: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    """Return filtered history entries, newest first."""
    entries = list(reversed(_load_history(snapshot_dir)))
    if snapshot_name:
        entries = [e for e in entries if e.get("snapshot") == snapshot_name]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    if limit is not None:
        entries = entries[:limit]
    return entries


def clear_history(snapshot_dir: str) -> int:
    """Delete all history entries. Returns number of entries removed."""
    entries = _load_history(snapshot_dir)
    count = len(entries)
    _save_history(snapshot_dir, [])
    return count
