"""Command-line interface for envsnap."""

import argparse
import sys

from envsnap import snapshot
from envsnap.diff import diff_snapshots, format_diff


def cmd_capture(args: argparse.Namespace) -> None:
    env = snapshot.capture()
    snapshot.save(env, args.name, snapshot_dir=args.dir)
    print(f"Snapshot '{args.name}' saved ({len(env)} variables).")


def cmd_list(args: argparse.Namespace) -> None:
    names = snapshot.list_snapshots(snapshot_dir=args.dir)
    if not names:
        print("No snapshots found.")
        return
    for name in sorted(names):
        print(name)


def cmd_delete(args: argparse.Namespace) -> None:
    snapshot.delete(args.name, snapshot_dir=args.dir)
    print(f"Snapshot '{args.name}' deleted.")


def cmd_diff(args: argparse.Namespace) -> None:
    snap_a = snapshot.load(args.snapshot_a, snapshot_dir=args.dir)
    snap_b = snapshot.load(args.snapshot_b, snapshot_dir=args.dir)
    diff = diff_snapshots(snap_a, snap_b)
    print(format_diff(diff, show_unchanged=args.show_unchanged))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsnap",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    parser.add_argument(
        "--dir",
        default=None,
        metavar="PATH",
        help="Directory to store snapshots (default: ~/.envsnap).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = sub.add_parser("capture", help="Capture the current environment.")
    p_capture.add_argument("name", help="Name for the snapshot.")
    p_capture.set_defaults(func=cmd_capture)

    # list
    p_list = sub.add_parser("list", help="List saved snapshots.")
    p_list.set_defaults(func=cmd_list)

    # delete
    p_delete = sub.add_parser("delete", help="Delete a snapshot.")
    p_delete.add_argument("name", help="Name of the snapshot to delete.")
    p_delete.set_defaults(func=cmd_delete)

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("snapshot_a", help="Base snapshot name.")
    p_diff.add_argument("snapshot_b", help="Target snapshot name.")
    p_diff.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Also display unchanged variables.",
    )
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
