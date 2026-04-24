"""Restore environment variables from a snapshot."""

import os
from typing import Dict, Optional, List

from envsnap.snapshot import load


def restore_snapshot(
    snapshot_name: str,
    snapshot_dir: str,
    keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Restore environment variables from a saved snapshot.

    Args:
        snapshot_name: Name of the snapshot to restore.
        snapshot_dir: Directory where snapshots are stored.
        keys: Optional list of keys to restore. If None, restore all keys.
        dry_run: If True, return the changes without applying them.

    Returns:
        A dict mapping variable names to their restored values.
    """
    snapshot = load(snapshot_name, snapshot_dir)

    if keys is not None:
        snapshot = {k: v for k, v in snapshot.items() if k in keys}

    if not dry_run:
        for key, value in snapshot.items():
            os.environ[key] = value

    return snapshot


def generate_export_script(snapshot: Dict[str, str], shell: str = "bash") -> str:
    """Generate a shell export script from a snapshot dict.

    Args:
        snapshot: Dict of environment variable names to values.
        shell: Target shell type ('bash', 'fish', or 'powershell').

    Returns:
        A string containing the shell-specific export commands.
    """
    if shell == "fish":
        lines = [f"set -x {k} {v!r}" for k, v in sorted(snapshot.items())]
    elif shell == "powershell":
        lines = [f"$env:{k} = {v!r}" for k, v in sorted(snapshot.items())]
    else:  # bash / sh default
        lines = [f"export {k}={v!r}" for k, v in sorted(snapshot.items())]

    return "\n".join(lines)
