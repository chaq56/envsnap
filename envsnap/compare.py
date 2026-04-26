"""compare.py — Multi-snapshot comparison utilities for envsnap.

Provides tools to compare more than two snapshots at once, identifying
variables that are consistent, divergent, or unique across a set of snapshots.
"""

from typing import Any

# Possible consistency states for a key across snapshots
CONSISTENCY_STATES = ("consistent", "divergent", "partial")


class CompareResult:
    """Holds the result of a multi-snapshot comparison."""

    def __init__(
        self,
        consistent: dict[str, str],
        divergent: dict[str, dict[str, str | None]],
        partial: dict[str, dict[str, str | None]],
    ) -> None:
        """
        Args:
            consistent: Keys whose value is identical in every snapshot.
            divergent:  Keys present in all snapshots but with differing values.
                        Maps key -> {snapshot_name: value}.
            partial:    Keys present in some but not all snapshots.
                        Maps key -> {snapshot_name: value or None}.
        """
        self.consistent = consistent
        self.divergent = divergent
        self.partial = partial

    def summary(self) -> dict[str, int]:
        """Return a count summary of each category."""
        return {
            "consistent": len(self.consistent),
            "divergent": len(self.divergent),
            "partial": len(self.partial),
        }

    def as_dict(self) -> dict[str, Any]:
        """Serialise the result to a plain dictionary."""
        return {
            "consistent": self.consistent,
            "divergent": self.divergent,
            "partial": self.partial,
        }


def compare_snapshots(snapshots: list[dict]) -> CompareResult:
    """Compare two or more snapshots and classify every key.

    Args:
        snapshots: List of snapshot dicts as returned by ``snapshot.load``.
                   Each must contain at least ``"name"`` and ``"env"`` keys.

    Returns:
        A :class:`CompareResult` instance.

    Raises:
        ValueError: If fewer than two snapshots are supplied.
    """
    if len(snapshots) < 2:
        raise ValueError("compare_snapshots requires at least two snapshots.")

    names: list[str] = [s["name"] for s in snapshots]
    envs: list[dict[str, str]] = [s.get("env", {}) for s in snapshots]

    # Collect the union of all keys across every snapshot
    all_keys: set[str] = set()
    for env in envs:
        all_keys.update(env.keys())

    consistent: dict[str, str] = {}
    divergent: dict[str, dict[str, str | None]] = {}
    partial: dict[str, dict[str, str | None]] = {}

    for key in sorted(all_keys):
        # Build a mapping of snapshot_name -> value (None if absent)
        value_map: dict[str, str | None] = {
            name: env.get(key) for name, env in zip(names, envs)
        }

        present_values = [v for v in value_map.values() if v is not None]
        all_present = len(present_values) == len(snapshots)
        unique_values = set(present_values)

        if all_present and len(unique_values) == 1:
            # Same value in every snapshot
            consistent[key] = present_values[0]
        elif all_present:
            # Present everywhere but values differ
            divergent[key] = value_map  # type: ignore[assignment]
        else:
            # Missing from at least one snapshot
            partial[key] = value_map

    return CompareResult(consistent=consistent, divergent=divergent, partial=partial)


def format_compare(result: CompareResult, *, show_consistent: bool = False) -> str:
    """Render a :class:`CompareResult` as a human-readable string.

    Args:
        result:          The comparison result to format.
        show_consistent: When *True*, also list keys that are consistent
                         across all snapshots (omitted by default to reduce noise).

    Returns:
        A formatted multi-line string suitable for CLI output.
    """
    lines: list[str] = []

    if result.divergent:
        lines.append("=== Divergent (present in all, values differ) ===")
        for key, values in result.divergent.items():
            lines.append(f"  {key}")
            for snap_name, value in values.items():
                lines.append(f"    [{snap_name}] {value}")

    if result.partial:
        lines.append("=== Partial (missing from one or more snapshots) ===")
        for key, values in result.partial.items():
            lines.append(f"  {key}")
            for snap_name, value in values.items():
                display = value if value is not None else "<absent>"
                lines.append(f"    [{snap_name}] {display}")

    if show_consistent and result.consistent:
        lines.append("=== Consistent (same value everywhere) ===")
        for key, value in result.consistent.items():
            lines.append(f"  {key}={value}")

    summary = result.summary()
    lines.append(
        f"\nSummary: {summary['consistent']} consistent, "
        f"{summary['divergent']} divergent, "
        f"{summary['partial']} partial"
    )

    return "\n".join(lines)
