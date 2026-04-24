"""Core snapshot module for capturing and storing environment variable sets."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envsnap" / "snapshots"


def capture(name: str, env: Optional[dict] = None) -> dict:
    """Capture the current environment (or a provided dict) as a named snapshot."""
    variables = env if env is not None else dict(os.environ)
    snapshot = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "variables": variables,
    }
    return snapshot


def save(snapshot: dict, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as a JSON file."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    file_path = snapshot_dir / f"{snapshot['name']}.json"
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
    return file_path


def load(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> dict:
    """Load a snapshot by name from disk."""
    file_path = snapshot_dir / f"{name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def list_snapshots(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> list[str]:
    """Return a list of all saved snapshot names."""
    if not snapshot_dir.exists():
        return []
    return [
        p.stem
        for p in sorted(snapshot_dir.glob("*.json"))
        if p.is_file()
    ]


def delete(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> None:
    """Remove a snapshot by name from disk."""
    file_path = snapshot_dir / f"{name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    file_path.unlink()
