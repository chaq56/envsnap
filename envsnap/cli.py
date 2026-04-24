"""CLI entry points for envsnap."""

import sys
import json
import argparse

from envsnap import snapshot, diff, restore, export
from envsnap.merge import merge_snapshots, MergeConflictError


def cmd_capture(args):
    env = snapshot.capture()
    snap = snapshot.save(env, args.name, args.dir)
    print(f"Snapshot '{snap['name']}' saved to {args.dir}")


def cmd_list(args):
    snaps = snapshot.list_snapshots(args.dir)
    if not snaps:
        print("No snapshots found.")
    for s in snaps:
        print(f"  {s['name']}  ({s['timestamp']})")


def cmd_delete(args):
    snapshot.delete(args.name, args.dir)
    print(f"Deleted snapshot '{args.name}'.")


def cmd_diff(args):
    base = snapshot.load(args.base, args.dir)
    target = snapshot.load(args.target, args.dir)
    result = diff.diff_snapshots(base, target)
    print(diff.format_diff(result))


def cmd_restore(args):
    snap = snapshot.load(args.name, args.dir)
    keys = args.keys.split(",") if args.keys else None
    script = restore.generate_export_script(snap, keys=keys)
    if args.dry_run:
        print(script)
    else:
        restore.restore_snapshot(snap, keys=keys)
        print(f"Restored {len(snap['env'])} variable(s) from '{args.name}'.")


def cmd_export(args):
    snap = snapshot.load(args.name, args.dir)
    output = export.export_snapshot(snap, fmt=args.format)
    print(output)


def cmd_merge(args):
    """Merge two or more snapshots into a new named snapshot."""
    names = args.snapshots
    if len(names) < 2:
        print("Error: provide at least two snapshot names to merge.", file=sys.stderr)
        sys.exit(1)

    snaps = [snapshot.load(name, args.dir) for name in names]

    try:
        merged = merge_snapshots(snaps, strategy=args.strategy, label=args.output)
    except MergeConflictError as exc:
        print(f"Merge conflict: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.save:
        saved = snapshot.save(merged["env"], merged["name"], args.dir)
        print(f"Merged snapshot saved as '{saved['name']}' in {args.dir}")
        if merged["conflicts"]:
            print(f"  Conflicts resolved via '{args.strategy}': {list(merged['conflicts'].keys())}")
    else:
        print(json.dumps(merged, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(prog="envsnap", description="Snapshot and manage environment variables.")
    parser.add_argument("--dir", default=".envsnap", help="Snapshot storage directory.")
    sub = parser.add_subparsers(dest="command")

    p_capture = sub.add_parser("capture", help="Capture current environment.")
    p_capture.add_argument("name", help="Snapshot name.")
    p_capture.set_defaults(func=cmd_capture)

    p_list = sub.add_parser("list", help="List saved snapshots.")
    p_list.set_defaults(func=cmd_list)

    p_delete = sub.add_parser("delete", help="Delete a snapshot.")
    p_delete.add_argument("name")
    p_delete.set_defaults(func=cmd_delete)

    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("base")
    p_diff.add_argument("target")
    p_diff.set_defaults(func=cmd_diff)

    p_restore = sub.add_parser("restore", help="Restore a snapshot.")
    p_restore.add_argument("name")
    p_restore.add_argument("--keys", default=None)
    p_restore.add_argument("--dry-run", action="store_true")
    p_restore.set_defaults(func=cmd_restore)

    p_export = sub.add_parser("export", help="Export a snapshot.")
    p_export.add_argument("name")
    p_export.add_argument("--format", default="dotenv")
    p_export.set_defaults(func=cmd_export)

    p_merge = sub.add_parser("merge", help="Merge multiple snapshots.")
    p_merge.add_argument("snapshots", nargs="+", help="Snapshot names to merge (in order).")
    p_merge.add_argument("--strategy", default="last_wins", choices=["last_wins", "first_wins", "error_on_conflict"])
    p_merge.add_argument("--output", default=None, help="Name for the merged snapshot.")
    p_merge.add_argument("--save", action="store_true", help="Persist merged snapshot to disk.")
    p_merge.set_defaults(func=cmd_merge)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
