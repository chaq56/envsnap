"""Export snapshots to various formats (dotenv, shell, JSON)."""

import json
from typing import Dict, Optional

SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_snapshot(
    snapshot: Dict[str, str],
    fmt: str = "dotenv",
    prefix: Optional[str] = None,
) -> str:
    """Serialize a snapshot dict to the requested format string.

    Args:
        snapshot: Mapping of env-var name -> value.
        fmt: One of 'dotenv', 'shell', or 'json'.
        prefix: Optional prefix to filter keys (only keys starting with
                prefix are included).

    Returns:
        Formatted string representation of the snapshot.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    filtered = {
        k: v
        for k, v in snapshot.items()
        if prefix is None or k.startswith(prefix)
    }

    if fmt == "dotenv":
        return _to_dotenv(filtered)
    if fmt == "shell":
        return _to_shell(filtered)
    if fmt == "json":
        return json.dumps(filtered, indent=2)

    return ""  # unreachable, satisfies type checkers


def _escape_value(value: str) -> str:
    """Wrap value in double-quotes, escaping inner double-quotes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _to_dotenv(snapshot: Dict[str, str]) -> str:
    lines = [f"{k}={_escape_value(v)}" for k, v in sorted(snapshot.items())]
    return "\n".join(lines)


def _to_shell(snapshot: Dict[str, str]) -> str:
    lines = [f"export {k}={_escape_value(v)}" for k, v in sorted(snapshot.items())]
    return "\n".join(lines)
