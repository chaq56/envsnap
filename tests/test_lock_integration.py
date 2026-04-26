"""Integration tests: lock interacts correctly with snapshot save/delete guards."""

import json
from pathlib import Path

import pytest

from envsnap.lock import LockError, assert_unlocked, is_locked, lock_snapshot, unlock_snapshot


@pytest.fixture
def snap():
    return {
        "name": "prod",
        "env": {"DB_HOST": "db.prod", "SECRET": "s3cr3t"},
        "tags": ["production"],
    }


def test_full_lock_unlock_cycle(snap):
    locked = lock_snapshot(snap)
    assert is_locked(locked)
    unlocked = unlock_snapshot(locked)
    assert not is_locked(unlocked)


def test_assert_unlocked_blocks_delete_on_locked(snap):
    locked = lock_snapshot(snap)
    with pytest.raises(LockError, match="delete"):
        assert_unlocked(locked, operation="delete")


def test_assert_unlocked_blocks_save_on_locked(snap):
    locked = lock_snapshot(snap)
    with pytest.raises(LockError, match="save"):
        assert_unlocked(locked, operation="save")


def test_locked_snapshot_persists_to_disk(tmp_path, snap):
    locked = lock_snapshot(snap)
    path = tmp_path / "prod.json"
    with open(path, "w") as fh:
        json.dump(locked, fh)
    with open(path) as fh:
        reloaded = json.load(fh)
    assert is_locked(reloaded)


def test_unlocked_snapshot_persists_correctly(tmp_path, snap):
    locked = lock_snapshot(snap)
    unlocked = unlock_snapshot(locked)
    path = tmp_path / "prod.json"
    with open(path, "w") as fh:
        json.dump(unlocked, fh)
    with open(path) as fh:
        reloaded = json.load(fh)
    assert not is_locked(reloaded)
    assert "locked" not in reloaded


def test_lock_does_not_alter_env_values(snap):
    locked = lock_snapshot(snap)
    assert locked["env"] == snap["env"]


def test_double_lock_is_idempotent(snap):
    once = lock_snapshot(snap)
    twice = lock_snapshot(once)
    assert twice["locked"] is True
    assert list(k for k in twice if k == "locked") == ["locked"]
