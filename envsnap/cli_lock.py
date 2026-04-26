"""CLI commands for locking and unlocking snapshots."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from envsnap.lock import LockError, is_locked, lock_snapshot, unlock_snapshot


def _load_snapshot(snap_dir: str, name: str) -> dict:
    path = Path(snap_dir) / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found in {snap_dir}")
    with open(path) as fh:
        return json.load(fh)


def _save_snapshot(snap_dir: str, name: str, data: dict) -> None:
    path = Path(snap_dir) / f"{name}.json"
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def cmd_lock(args: argparse.Namespace) -> None:
    """Lock a snapshot so it cannot be modified or deleted."""
    snap_dir = args.snap_dir
    try:
        snap = _load_snapshot(snap_dir, args.name)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    if is_locked(snap):
        print(f"Snapshot '{args.name}' is already locked.")
        return

    updated = lock_snapshot(snap)
    _save_snapshot(snap_dir, args.name, updated)
    print(f"Snapshot '{args.name}' locked.")


def cmd_unlock(args: argparse.Namespace) -> None:
    """Unlock a previously locked snapshot."""
    snap_dir = args.snap_dir
    try:
        snap = _load_snapshot(snap_dir, args.name)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    if not is_locked(snap):
        print(f"Snapshot '{args.name}' is not locked.")
        return

    updated = unlock_snapshot(snap)
    _save_snapshot(snap_dir, args.name, updated)
    print(f"Snapshot '{args.name}' unlocked.")


def cmd_lock_status(args: argparse.Namespace) -> None:
    """Print the lock status of a snapshot."""
    snap_dir = args.snap_dir
    try:
        snap = _load_snapshot(snap_dir, args.name)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    status = "locked" if is_locked(snap) else "unlocked"
    print(f"Snapshot '{args.name}' is {status}.")


def register_lock_commands(subparsers, snap_dir: str) -> None:
    """Register lock/unlock subcommands onto an argparse subparser group."""
    for cmd_name, func, help_text in [
        ("lock", cmd_lock, "Lock a snapshot"),
        ("unlock", cmd_unlock, "Unlock a snapshot"),
        ("lock-status", cmd_lock_status, "Show lock status of a snapshot"),
    ]:
        p = subparsers.add_parser(cmd_name, help=help_text)
        p.add_argument("name", help="Snapshot name")
        p.set_defaults(func=func, snap_dir=snap_dir)
