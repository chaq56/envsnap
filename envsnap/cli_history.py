"""CLI commands for snapshot history."""

from __future__ import annotations

import argparse
import os
from typing import Optional

from envsnap.history import get_history, clear_history

DEFAULT_SNAPSHOT_DIR = os.path.expanduser("~/.envsnap")


def cmd_history_show(args: argparse.Namespace) -> None:
    """Print history entries to stdout."""
    snapshot_dir = getattr(args, "dir", DEFAULT_SNAPSHOT_DIR)
    snapshot_name: Optional[str] = getattr(args, "snapshot", None)
    action: Optional[str] = getattr(args, "action", None)
    limit: Optional[int] = getattr(args, "limit", None)

    entries = get_history(
        snapshot_dir,
        snapshot_name=snapshot_name,
        action=action,
        limit=limit,
    )

    if not entries:
        print("No history entries found.")
        return

    for entry in entries:
        parts = [entry["timestamp"], entry["action"].upper(), entry["snapshot"]]
        if "detail" in entry:
            parts.append(f"({entry['detail']})")
        print("  ".join(parts))


def cmd_history_clear(args: argparse.Namespace) -> None:
    """Clear all history entries."""
    snapshot_dir = getattr(args, "dir", DEFAULT_SNAPSHOT_DIR)
    count = clear_history(snapshot_dir)
    print(f"Cleared {count} history entry/entries.")


def register_history_commands(subparsers: argparse._SubParsersAction) -> None:
    """Attach history sub-commands to an existing subparser."""
    history_parser = subparsers.add_parser("history", help="Manage snapshot history")
    history_sub = history_parser.add_subparsers(dest="history_cmd")

    show_parser = history_sub.add_parser("show", help="Show history log")
    show_parser.add_argument("--snapshot", metavar="NAME", help="Filter by snapshot name")
    show_parser.add_argument("--action", metavar="ACTION", help="Filter by action type")
    show_parser.add_argument("--limit", type=int, metavar="N", help="Limit number of results")
    show_parser.add_argument("--dir", default=DEFAULT_SNAPSHOT_DIR, help="Snapshot directory")
    show_parser.set_defaults(func=cmd_history_show)

    clear_parser = history_sub.add_parser("clear", help="Clear all history")
    clear_parser.add_argument("--dir", default=DEFAULT_SNAPSHOT_DIR, help="Snapshot directory")
    clear_parser.set_defaults(func=cmd_history_clear)
