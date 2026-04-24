"""CLI entry point for envsnap."""

import argparse
import sys

from envsnap.snapshot import capture, save, load, list_snapshots, delete
from envsnap.diff import diff_snapshots, format_diff
from envsnap.restore import restore_snapshot, generate_export_script

DEFAULT_SNAPSHOT_DIR = ".envsnap"


def cmd_capture(args):
    snapshot = capture()
    save(args.name, snapshot, args.dir)
    print(f"Snapshot '{args.name}' saved to {args.dir}")


def cmd_list(args):
    names = list_snapshots(args.dir)
    if not names:
        print("No snapshots found.")
    else:
        for name in names:
            print(name)


def cmd_delete(args):
    delete(args.name, args.dir)
    print(f"Snapshot '{args.name}' deleted.")


def cmd_diff(args):
    base = load(args.base, args.dir)
    target = load(args.target, args.dir)
    result = diff_snapshots(base, target)
    print(format_diff(result))


def cmd_restore(args):
    keys = args.keys.split(",") if args.keys else None
    restored = restore_snapshot(
        args.name, args.dir, keys=keys, dry_run=args.dry_run
    )
    if args.export:
        print(generate_export_script(restored, shell=args.shell))
    elif args.dry_run:
        for k, v in sorted(restored.items()):
            print(f"{k}={v}")
    else:
        print(f"Restored {len(restored)} variable(s) from snapshot '{args.name}'.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envsnap",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    parser.add_argument(
        "--dir", default=DEFAULT_SNAPSHOT_DIR, help="Snapshot storage directory."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = sub.add_parser("capture", help="Capture current environment.")
    p_capture.add_argument("name", help="Snapshot name.")
    p_capture.set_defaults(func=cmd_capture)

    # list
    p_list = sub.add_parser("list", help="List saved snapshots.")
    p_list.set_defaults(func=cmd_list)

    # delete
    p_delete = sub.add_parser("delete", help="Delete a snapshot.")
    p_delete.add_argument("name", help="Snapshot name.")
    p_delete.set_defaults(func=cmd_delete)

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("base", help="Base snapshot name.")
    p_diff.add_argument("target", help="Target snapshot name.")
    p_diff.set_defaults(func=cmd_diff)

    # restore
    p_restore = sub.add_parser("restore", help="Restore a snapshot.")
    p_restore.add_argument("name", help="Snapshot name.")
    p_restore.add_argument("--keys", help="Comma-separated list of keys to restore.")
    p_restore.add_argument("--dry-run", action="store_true", help="Preview without applying.")
    p_restore.add_argument("--export", action="store_true", help="Print export script.")
    p_restore.add_argument("--shell", default="bash", choices=["bash", "fish", "powershell"])
    p_restore.set_defaults(func=cmd_restore)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
