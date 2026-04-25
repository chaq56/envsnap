"""CLI sub-commands for snapshot tag management."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from envsnap.tag import TagError, add_tag, filter_snapshots_by_tag, list_tags, remove_tag, tags_index


def _load_snapshot(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_snapshot(path: Path, snapshot: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)


def cmd_tag_add(name: str, tag: str, snapshot_dir: Path) -> None:
    """Add *tag* to the snapshot named *name*."""
    path = snapshot_dir / f"{name}.json"
    if not path.exists():
        print(f"Error: snapshot '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    try:
        snap = _load_snapshot(path)
        updated = add_tag(snap, tag)
        _save_snapshot(path, updated)
        print(f"Tag '{tag}' added to snapshot '{name}'.")
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_remove(name: str, tag: str, snapshot_dir: Path) -> None:
    """Remove *tag* from the snapshot named *name*."""
    path = snapshot_dir / f"{name}.json"
    if not path.exists():
        print(f"Error: snapshot '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    try:
        snap = _load_snapshot(path)
        updated = remove_tag(snap, tag)
        _save_snapshot(path, updated)
        print(f"Tag '{tag}' removed from snapshot '{name}'.")
    except TagError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_list(name: str, snapshot_dir: Path) -> None:
    """List tags for the snapshot named *name*."""
    path = snapshot_dir / f"{name}.json"
    if not path.exists():
        print(f"Error: snapshot '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    snap = _load_snapshot(path)
    tags = list_tags(snap)
    if tags:
        print("\n".join(tags))
    else:
        print(f"No tags for snapshot '{name}'.")


def cmd_tag_filter(tag: str, snapshot_dir: Path) -> None:
    """List all snapshots that carry *tag*."""
    snapshots = []
    for p in sorted(snapshot_dir.glob("*.json")):
        try:
            snapshots.append(_load_snapshot(p))
        except (json.JSONDecodeError, OSError):
            continue
    matches = filter_snapshots_by_tag(snapshots, tag)
    if matches:
        for s in matches:
            print(s.get("name", p.stem))
    else:
        print(f"No snapshots found with tag '{tag}'.")


def cmd_tag_index(snapshot_dir: Path) -> None:
    """Print a tag -> snapshots index for all saved snapshots."""
    snapshots = []
    for p in sorted(snapshot_dir.glob("*.json")):
        try:
            snapshots.append(_load_snapshot(p))
        except (json.JSONDecodeError, OSError):
            continue
    index = tags_index(snapshots)
    if not index:
        print("No tags found.")
        return
    for tag, names in sorted(index.items()):
        print(f"{tag}: {', '.join(sorted(names))}")
