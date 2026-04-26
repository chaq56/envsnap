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


def diff(name_a: str, name_b: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> dict:
    """Compare two snapshots and return the differences between their variables.

    Returns a dict with three keys:
      - 'added':   variables present in name_b but not in name_a
      - 'removed': variables present in name_a but not in name_b
      - 'changed': variables present in both but with different values,
                   as {key: {"from": old_value, "to": new_value}}
    """
    vars_a = load(name_a, snapshot_dir)["variables"]
    vars_b = load(name_b, snapshot_dir)["variables"]

    keys_a = set(vars_a)
    keys_b = set(vars_b)

    return {
        "added": {k: vars_b[k] for k in keys_b - keys_a},
        "removed": {k: vars_a[k] for k in keys_a - keys_b},
        "changed": {
            k: {"from": vars_a[k], "to": vars_b[k]}
            for k in keys_a & keys_b
            if vars_a[k] != vars_b[k]
        },
    }
