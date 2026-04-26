"""Tests for envsnap.history module."""

import json
import pytest
from pathlib import Path

from envsnap.history import (
    record_event,
    get_history,
    clear_history,
    HISTORY_FILENAME,
    MAX_HISTORY_ENTRIES,
    _history_path,
)


@pytest.fixture
def snap_dir(tmp_path):
    return str(tmp_path / "snapshots")


def test_record_event_creates_history_file(snap_dir):
    record_event(snap_dir, "capture", "mysnap")
    assert _history_path(snap_dir).exists()


def test_record_event_returns_entry(snap_dir):
    entry = record_event(snap_dir, "capture", "mysnap")
    assert entry["action"] == "capture"
    assert entry["snapshot"] == "mysnap"
    assert "timestamp" in entry


def test_record_event_stores_detail(snap_dir):
    entry = record_event(snap_dir, "export", "mysnap", detail="dotenv")
    assert entry["detail"] == "dotenv"


def test_record_event_unknown_action_raises(snap_dir):
    with pytest.raises(ValueError, match="Unknown action"):
        record_event(snap_dir, "frobnicate", "mysnap")


def test_get_history_returns_newest_first(snap_dir):
    record_event(snap_dir, "capture", "snap1")
    record_event(snap_dir, "load", "snap2")
    history = get_history(snap_dir)
    assert history[0]["action"] == "load"
    assert history[1]["action"] == "capture"


def test_get_history_filters_by_snapshot(snap_dir):
    record_event(snap_dir, "capture", "alpha")
    record_event(snap_dir, "capture", "beta")
    results = get_history(snap_dir, snapshot_name="alpha")
    assert all(e["snapshot"] == "alpha" for e in results)
    assert len(results) == 1


def test_get_history_filters_by_action(snap_dir):
    record_event(snap_dir, "capture", "snap")
    record_event(snap_dir, "delete", "snap")
    results = get_history(snap_dir, action="delete")
    assert len(results) == 1
    assert results[0]["action"] == "delete"


def test_get_history_respects_limit(snap_dir):
    for i in range(10):
        record_event(snap_dir, "load", f"snap{i}")
    results = get_history(snap_dir, limit=3)
    assert len(results) == 3


def test_get_history_empty_dir_returns_empty_list(snap_dir):
    assert get_history(snap_dir) == []


def test_clear_history_returns_count(snap_dir):
    record_event(snap_dir, "capture", "s1")
    record_event(snap_dir, "capture", "s2")
    count = clear_history(snap_dir)
    assert count == 2


def test_clear_history_empties_file(snap_dir):
    record_event(snap_dir, "capture", "s1")
    clear_history(snap_dir)
    assert get_history(snap_dir) == []


def test_history_trimmed_to_max_entries(snap_dir, monkeypatch):
    monkeypatch.setattr("envsnap.history.MAX_HISTORY_ENTRIES", 5)
    for i in range(8):
        record_event(snap_dir, "load", f"snap{i}")
    raw = json.loads(_history_path(snap_dir).read_text())
    assert len(raw) == 5
