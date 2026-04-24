"""Merge multiple snapshots into a single combined snapshot."""

from typing import Optional

MERGE_STRATEGIES = ("last_wins", "first_wins", "error_on_conflict")


class MergeConflictError(Exception):
    """Raised when two snapshots have conflicting keys and strategy is 'error_on_conflict'."""

    def __init__(self, key: str, values: list):
        self.key = key
        self.values = values
        super().__init__(
            f"Conflict on key '{key}': values {values} cannot be merged with 'error_on_conflict' strategy."
        )


def merge_snapshots(
    snapshots: list[dict],
    strategy: str = "last_wins",
    label: Optional[str] = None,
) -> dict:
    """Merge a list of snapshot dicts into one.

    Args:
        snapshots: Ordered list of snapshot dicts (each has 'name', 'timestamp', 'env').
        strategy: One of 'last_wins', 'first_wins', 'error_on_conflict'.
        label: Optional name for the resulting merged snapshot.

    Returns:
        A new snapshot dict with merged 'env' and metadata.

    Raises:
        ValueError: If fewer than 2 snapshots are provided or strategy is unknown.
        MergeConflictError: If strategy is 'error_on_conflict' and a key conflict is found.
    """
    if strategy not in MERGE_STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy}'. Choose from {MERGE_STRATEGIES}.")
    if len(snapshots) < 2:
        raise ValueError("At least two snapshots are required for a merge.")

    merged_env: dict[str, str] = {}
    conflict_tracker: dict[str, list[str]] = {}

    for snapshot in snapshots:
        for key, value in snapshot.get("env", {}).items():
            if key in merged_env and merged_env[key] != value:
                conflict_tracker.setdefault(key, [merged_env[key]])
                conflict_tracker[key].append(value)

                if strategy == "error_on_conflict":
                    raise MergeConflictError(key, conflict_tracker[key])
                elif strategy == "last_wins":
                    merged_env[key] = value
                # first_wins: keep existing value, do nothing
            else:
                merged_env[key] = value

    source_names = [s.get("name", "unknown") for s in snapshots]
    return {
        "name": label or f"merged({'_'.join(source_names)})",
        "timestamp": None,
        "sources": source_names,
        "strategy": strategy,
        "conflicts": {
            k: v for k, v in conflict_tracker.items() if strategy != "error_on_conflict"
        },
        "env": merged_env,
    }
