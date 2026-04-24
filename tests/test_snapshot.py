"""Tests for envsnap.snapshot module."""

import json
import pytest
from pathlib import Path

from envsnap.snapshot import capture, save, load, list_snapshots, delete


SAMPLE_ENV = {
    "HOME": "/home/user",
    "PATH": "/usr/bin:/bin",
    "DEBUG": "true",
}


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_capture_returns_expected_keys():
    snap = capture("test-snap", env=SAMPLE_ENV)
    assert snap["name"] == "test-snap"
    assert "created_at" in snap
    assert snap["variables"] == SAMPLE_ENV


def test_capture_uses_os_environ_when_env_not_provided():
    import os
    snap = capture("env-snap")
    assert snap["variables"] == dict(os.environ)


def test_save_creates_json_file(snapshot_dir):
    snap = capture("my-project", env=SAMPLE_ENV)
    path = save(snap, snapshot_dir=snapshot_dir)
    assert path.exists()
    assert path.suffix == ".json"
    data = json.loads(path.read_text())
    assert data["name"] == "my-project"


def test_load_returns_correct_snapshot(snapshot_dir):
    snap = capture("load-test", env=SAMPLE_ENV)
    save(snap, snapshot_dir=snapshot_dir)
    loaded = load("load-test", snapshot_dir=snapshot_dir)
    assert loaded["variables"] == SAMPLE_ENV


def test_load_raises_when_missing(snapshot_dir):
    with pytest.raises(FileNotFoundError, match="ghost"):
        load("ghost", snapshot_dir=snapshot_dir)


def test_list_snapshots_empty(snapshot_dir):
    assert list_snapshots(snapshot_dir=snapshot_dir) == []


def test_list_snapshots_returns_names(snapshot_dir):
    for name in ("alpha", "beta", "gamma"):
        save(capture(name, env=SAMPLE_ENV), snapshot_dir=snapshot_dir)
    names = list_snapshots(snapshot_dir=snapshot_dir)
    assert names == ["alpha", "beta", "gamma"]


def test_delete_removes_file(snapshot_dir):
    snap = capture("to-delete", env=SAMPLE_ENV)
    save(snap, snapshot_dir=snapshot_dir)
    delete("to-delete", snapshot_dir=snapshot_dir)
    assert "to-delete" not in list_snapshots(snapshot_dir=snapshot_dir)


def test_delete_raises_when_missing(snapshot_dir):
    with pytest.raises(FileNotFoundError):
        delete("nonexistent", snapshot_dir=snapshot_dir)
