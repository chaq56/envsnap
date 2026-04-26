"""Tests for envsnap.cli_history module."""

import argparse
import pytest

from envsnap.history import record_event
from envsnap.cli_history import cmd_history_show, cmd_history_clear, register_history_commands


@pytest.fixture
def snap_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return str(d)


def _make_args(snap_dir, **kwargs):
    ns = argparse.Namespace(dir=snap_dir, snapshot=None, action=None, limit=None)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cmd_history_show_empty(snap_dir, capsys):
    cmd_history_show(_make_args(snap_dir))
    out = capsys.readouterr().out
    assert "No history entries found" in out


def test_cmd_history_show_lists_entries(snap_dir, capsys):
    record_event(snap_dir, "capture", "mysnap")
    cmd_history_show(_make_args(snap_dir))
    out = capsys.readouterr().out
    assert "CAPTURE" in out
    assert "mysnap" in out


def test_cmd_history_show_filter_by_snapshot(snap_dir, capsys):
    record_event(snap_dir, "capture", "alpha")
    record_event(snap_dir, "capture", "beta")
    cmd_history_show(_make_args(snap_dir, snapshot="alpha"))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" not in out


def test_cmd_history_show_filter_by_action(snap_dir, capsys):
    record_event(snap_dir, "capture", "snap")
    record_event(snap_dir, "delete", "snap")
    cmd_history_show(_make_args(snap_dir, action="delete"))
    out = capsys.readouterr().out
    assert "DELETE" in out
    assert "CAPTURE" not in out


def test_cmd_history_show_limit(snap_dir, capsys):
    for i in range(5):
        record_event(snap_dir, "load", f"snap{i}")
    cmd_history_show(_make_args(snap_dir, limit=2))
    out = capsys.readouterr().out
    assert out.count("LOAD") == 2


def test_cmd_history_show_includes_detail(snap_dir, capsys):
    record_event(snap_dir, "export", "snap", detail="shell")
    cmd_history_show(_make_args(snap_dir))
    out = capsys.readouterr().out
    assert "shell" in out


def test_cmd_history_clear_reports_count(snap_dir, capsys):
    record_event(snap_dir, "capture", "s1")
    record_event(snap_dir, "capture", "s2")
    cmd_history_clear(_make_args(snap_dir))
    out = capsys.readouterr().out
    assert "2" in out


def test_cmd_history_clear_empties_history(snap_dir, capsys):
    record_event(snap_dir, "capture", "s1")
    cmd_history_clear(_make_args(snap_dir))
    cmd_history_show(_make_args(snap_dir))
    out = capsys.readouterr().out
    assert "No history entries found" in out


def test_register_history_commands_attaches_subparser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    register_history_commands(subs)
    args = parser.parse_args(["history", "show"])
    assert args.cmd == "history"
