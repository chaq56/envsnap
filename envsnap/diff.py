"""Diff two environment snapshots and report added, removed, and changed variables."""

from typing import Any


def diff_snapshots(
    snapshot_a: dict[str, str],
    snapshot_b: dict[str, str],
) -> dict[str, Any]:
    """Compare two snapshots and return a structured diff.

    Args:
        snapshot_a: The base snapshot (e.g. older / left side).
        snapshot_b: The target snapshot (e.g. newer / right side).

    Returns:
        A dict with keys:
            - 'added':   vars present in b but not in a  {key: new_value}
            - 'removed': vars present in a but not in b  {key: old_value}
            - 'changed': vars whose value differs         {key: (old_value, new_value)}
            - 'unchanged': vars identical in both         {key: value}
    """
    keys_a = set(snapshot_a.keys())
    keys_b = set(snapshot_b.keys())

    added = {k: snapshot_b[k] for k in keys_b - keys_a}
    removed = {k: snapshot_a[k] for k in keys_a - keys_b}
    changed = {
        k: (snapshot_a[k], snapshot_b[k])
        for k in keys_a & keys_b
        if snapshot_a[k] != snapshot_b[k]
    }
    unchanged = {
        k: snapshot_a[k]
        for k in keys_a & keys_b
        if snapshot_a[k] == snapshot_b[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: dict[str, Any], show_unchanged: bool = False) -> str:
    """Render a diff dict as a human-readable string.

    Args:
        diff: Output from :func:`diff_snapshots`.
        show_unchanged: Whether to include unchanged variables in output.

    Returns:
        A formatted multi-line string.
    """
    lines: list[str] = []

    for key, value in sorted(diff["added"].items()):
        lines.append(f"+ {key}={value}")

    for key, value in sorted(diff["removed"].items()):
        lines.append(f"- {key}={value}")

    for key, (old, new) in sorted(diff["changed"].items()):
        lines.append(f"~ {key}: {old!r} -> {new!r}")

    if show_unchanged:
        for key, value in sorted(diff["unchanged"].items()):
            lines.append(f"  {key}={value}")

    if not lines:
        return "No differences found."

    return "\n".join(lines)
