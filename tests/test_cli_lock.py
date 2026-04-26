"""Tests for envsnap.cli_lock module."""

import argparse
import json
from pathlib import Path

import pytest

from envsnap.cli_lock import cmd_lock, cmd_lock_status, cmd_unlock


@pytest.fixture
def snap_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(snap_dir: str, data: dict) -> None:
    path = Path(snap_dir) / f"{data['name']}.json"
    with open(path, "w") as fh:
        json.dump(data, fh)


def _read_snapshot(snap_dir: str, name: str) -> dict:
    path = Path(snap_dir) / f"{name}.json"
    with open(path) as fh:
        return json.load(fh)


def _make_args(snap_dir, name):
    ns = argparse.Namespace()
    ns.snap_dir = snap_dir
    ns.name = name
    return ns


def test_cmd_lock_sets_locked(snap_dir):
    _write_snapshot(snap_dir, {"name": "dev", "env": {}, "tags": []})
    cmd_lock(_make_args(snap_dir, "dev"))
    snap = _read_snapshot(snap_dir, "dev")
    assert snap["locked"] is True


def test_cmd_lock_already_locked_prints_message(snap_dir, capsys):
    _write_snapshot(snap_dir, {"name": "dev", "env": {}, "locked": True})
    cmd_lock(_make_args(snap_dir, "dev"))
    out = capsys.readouterr().out
    assert "already locked" in out


def test_cmd_lock_missing_snapshot_prints_error(snap_dir, capsys):
    cmd_lock(_make_args(snap_dir, "ghost"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_unlock_removes_locked(snap_dir):
    _write_snapshot(snap_dir, {"name": "dev", "env": {}, "locked": True})
    cmd_unlock(_make_args(snap_dir, "dev"))
    snap = _read_snapshot(snap_dir, "dev")
    assert "locked" not in snap


def test_cmd_unlock_not_locked_prints_message(snap_dir, capsys):
    _write_snapshot(snap_dir, {"name": "dev", "env": {}, "tags": []})
    cmd_unlock(_make_args(snap_dir, "dev"))
    out = capsys.readouterr().out
    assert "not locked" in out


def test_cmd_unlock_missing_snapshot_prints_error(snap_dir, capsys):
    cmd_unlock(_make_args(snap_dir, "ghost"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_lock_status_locked(snap_dir, capsys):
    _write_snapshot(snap_dir, {"name": "dev", "env": {}, "locked": True})
    cmd_lock_status(_make_args(snap_dir, "dev"))
    out = capsys.readouterr().out
    assert "locked" in out


def test_cmd_lock_status_unlocked(snap_dir, capsys):
    _write_snapshot(snap_dir, {"name": "dev", "env": {}, "tags": []})
    cmd_lock_status(_make_args(snap_dir, "dev"))
    out = capsys.readouterr().out
    assert "unlocked" in out


def test_cmd_lock_status_missing_snapshot(snap_dir, capsys):
    cmd_lock_status(_make_args(snap_dir, "ghost"))
    out = capsys.readouterr().out
    assert "Error" in out
