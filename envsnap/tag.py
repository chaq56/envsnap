"""Tag management for envsnap snapshots."""

from __future__ import annotations

from typing import Dict, List

TAG_KEY = "_tags"


class TagError(Exception):
    """Raised when a tagging operation fails."""


def add_tag(snapshot: dict, tag: str) -> dict:
    """Return a copy of *snapshot* with *tag* added.

    Raises TagError if *tag* is empty or contains whitespace.
    """
    tag = tag.strip()
    if not tag:
        raise TagError("Tag must not be empty.")
    if " " in tag:
        raise TagError(f"Tag must not contain spaces: {tag!r}")

    updated = dict(snapshot)
    tags: List[str] = list(updated.get(TAG_KEY, []))
    if tag not in tags:
        tags.append(tag)
    updated[TAG_KEY] = sorted(tags)
    return updated


def remove_tag(snapshot: dict, tag: str) -> dict:
    """Return a copy of *snapshot* with *tag* removed.

    Raises TagError if *tag* is not present.
    """
    tags: List[str] = list(snapshot.get(TAG_KEY, []))
    if tag not in tags:
        raise TagError(f"Tag {tag!r} not found in snapshot.")
    tags.remove(tag)
    updated = dict(snapshot)
    updated[TAG_KEY] = sorted(tags)
    return updated


def list_tags(snapshot: dict) -> List[str]:
    """Return the list of tags attached to *snapshot*."""
    return list(snapshot.get(TAG_KEY, []))


def filter_snapshots_by_tag(snapshots: List[dict], tag: str) -> List[dict]:
    """Return snapshots that contain *tag*."""
    return [s for s in snapshots if tag in s.get(TAG_KEY, [])]


def tags_index(snapshots: List[dict]) -> Dict[str, List[str]]:
    """Build a mapping of tag -> list of snapshot names."""
    index: Dict[str, List[str]] = {}
    for snap in snapshots:
        name = snap.get("name", "<unnamed>")
        for tag in snap.get(TAG_KEY, []):
            index.setdefault(tag, []).append(name)
    return index
