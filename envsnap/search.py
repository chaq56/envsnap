"""Search and filter environment variable snapshots by key patterns or values."""

import fnmatch
import re
from typing import Any


SEARCH_MODES = ("key", "value", "both")


def search_snapshot(
    snapshot: dict[str, Any],
    pattern: str,
    mode: str = "both",
    use_regex: bool = False,
) -> dict[str, str]:
    """Search a snapshot for entries matching a pattern.

    Args:
        snapshot: A snapshot dict as returned by load().
        pattern: A glob or regex pattern to match against.
        mode: One of 'key', 'value', or 'both'.
        use_regex: If True, treat pattern as a regular expression.

    Returns:
        A dict of matching key-value pairs from snapshot['env'].

    Raises:
        ValueError: If mode is not one of SEARCH_MODES.
        re.error: If use_regex is True and pattern is invalid.
    """
    if mode not in SEARCH_MODES:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {SEARCH_MODES}")

    env: dict[str, str] = snapshot.get("env", {})

    if use_regex:
        compiled = re.compile(pattern)
        match_fn = lambda s: bool(compiled.search(s))
    else:
        match_fn = lambda s: fnmatch.fnmatch(s, pattern)

    results: dict[str, str] = {}
    for key, value in env.items():
        key_matches = match_fn(key) if mode in ("key", "both") else False
        value_matches = match_fn(value) if mode in ("value", "both") else False
        if key_matches or value_matches:
            results[key] = value

    return results


def search_across_snapshots(
    snapshots: list[dict[str, Any]],
    pattern: str,
    mode: str = "both",
    use_regex: bool = False,
) -> dict[str, dict[str, str]]:
    """Search multiple snapshots, returning matches grouped by snapshot name.

    Args:
        snapshots: List of snapshot dicts.
        pattern: A glob or regex pattern to match against.
        mode: One of 'key', 'value', or 'both'.
        use_regex: If True, treat pattern as a regular expression.

    Returns:
        A dict mapping snapshot name -> matching key-value pairs.
    """
    results: dict[str, dict[str, str]] = {}
    for snapshot in snapshots:
        name = snapshot.get("name", "unknown")
        matches = search_snapshot(snapshot, pattern, mode=mode, use_regex=use_regex)
        if matches:
            results[name] = matches
    return results
