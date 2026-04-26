"""Tests for envsnap.lock module."""

import pytest

from envsnap.lock import (
    LockError,
    assert_unlocked,
    is_locked,
    lock_snapshot,
    unlock_snapshot,
)


@pytest.fixture
def base_snapshot():
    return {
        "name": "mysnap",
        "env": {"HOME": "/home/user", "PATH": "/usr/bin"},
        "tags": [],
    }


def test_lock_sets_locked_true(base_snapshot):
    result = lock_snapshot(base_snapshot)
    assert result["locked"] is True


def test_lock_does_not_mutate_original(base_snapshot):
    lock_snapshot(base_snapshot)
    assert "locked" not in base_snapshot


def test_lock_preserves_other_fields(base_snapshot):
    result = lock_snapshot(base_snapshot)
    assert result["name"] == "mysnap"
    assert result["env"] == base_snapshot["env"]


def test_unlock_removes_locked_field(base_snapshot):
    locked = lock_snapshot(base_snapshot)
    result = unlock_snapshot(locked)
    assert "locked" not in result


def test_unlock_does_not_mutate_original(base_snapshot):
    locked = lock_snapshot(base_snapshot)
    unlock_snapshot(locked)
    assert locked["locked"] is True


def test_unlock_on_already_unlocked_snapshot(base_snapshot):
    result = unlock_snapshot(base_snapshot)
    assert "locked" not in result


def test_is_locked_returns_true_for_locked(base_snapshot):
    locked = lock_snapshot(base_snapshot)
    assert is_locked(locked) is True


def test_is_locked_returns_false_for_unlocked(base_snapshot):
    assert is_locked(base_snapshot) is False


def test_is_locked_returns_false_when_key_absent(base_snapshot):
    assert is_locked(base_snapshot) is False


def test_assert_unlocked_raises_for_locked(base_snapshot):
    locked = lock_snapshot(base_snapshot)
    with pytest.raises(LockError, match="mysnap"):
        assert_unlocked(locked)


def test_assert_unlocked_passes_for_unlocked(base_snapshot):
    assert_unlocked(base_snapshot)  # should not raise


def test_assert_unlocked_includes_operation_in_message(base_snapshot):
    locked = lock_snapshot(base_snapshot)
    with pytest.raises(LockError, match="delete"):
        assert_unlocked(locked, operation="delete")


def test_lock_raises_for_non_dict():
    with pytest.raises(LockError):
        lock_snapshot("not-a-dict")  # type: ignore


def test_unlock_raises_for_non_dict():
    with pytest.raises(LockError):
        unlock_snapshot(["not", "a", "dict"])  # type: ignore
