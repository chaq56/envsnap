"""Tests for envsnap.pin module."""

import pytest

from envsnap.pin import (
    PinError,
    PINNED_KEY,
    pin_keys,
    unpin_keys,
    list_pinned,
    is_pinned,
    filter_unpinned,
)


@pytest.fixture
def base_snapshot():
    return {
        "name": "test-snap",
        "env": {"HOME": "/home/user", "PATH": "/usr/bin", "DEBUG": "1"},
        PINNED_KEY: [],
    }


def test_pin_keys_adds_to_pinned(base_snapshot):
    result = pin_keys(base_snapshot, ["HOME"])
    assert "HOME" in result[PINNED_KEY]


def test_pin_keys_deduplicates(base_snapshot):
    snap = pin_keys(base_snapshot, ["HOME"])
    snap2 = pin_keys(snap, ["HOME"])
    assert snap2[PINNED_KEY].count("HOME") == 1


def test_pin_keys_is_sorted(base_snapshot):
    result = pin_keys(base_snapshot, ["PATH", "DEBUG"])
    assert result[PINNED_KEY] == sorted(result[PINNED_KEY])


def test_pin_keys_does_not_mutate_original(base_snapshot):
    pin_keys(base_snapshot, ["HOME"])
    assert base_snapshot[PINNED_KEY] == []


def test_pin_keys_raises_for_missing_key(base_snapshot):
    with pytest.raises(PinError, match="not found"):
        pin_keys(base_snapshot, ["NONEXISTENT"])


def test_pin_keys_raises_for_non_dict():
    with pytest.raises(PinError):
        pin_keys("not a dict", ["HOME"])


def test_unpin_keys_removes_pinned_key(base_snapshot):
    snap = pin_keys(base_snapshot, ["HOME", "PATH"])
    result = unpin_keys(snap, ["HOME"])
    assert "HOME" not in result[PINNED_KEY]
    assert "PATH" in result[PINNED_KEY]


def test_unpin_keys_raises_if_not_pinned(base_snapshot):
    with pytest.raises(PinError, match="not currently pinned"):
        unpin_keys(base_snapshot, ["HOME"])


def test_unpin_keys_does_not_mutate_original(base_snapshot):
    snap = pin_keys(base_snapshot, ["HOME"])
    unpin_keys(snap, ["HOME"])
    assert "HOME" in snap[PINNED_KEY]


def test_list_pinned_returns_empty_by_default(base_snapshot):
    assert list_pinned(base_snapshot) == []


def test_list_pinned_returns_pinned_keys(base_snapshot):
    snap = pin_keys(base_snapshot, ["DEBUG", "HOME"])
    assert set(list_pinned(snap)) == {"DEBUG", "HOME"}


def test_is_pinned_true(base_snapshot):
    snap = pin_keys(base_snapshot, ["PATH"])
    assert is_pinned(snap, "PATH") is True


def test_is_pinned_false(base_snapshot):
    assert is_pinned(base_snapshot, "PATH") is False


def test_filter_unpinned_excludes_pinned_keys(base_snapshot):
    snap = pin_keys(base_snapshot, ["HOME"])
    result = filter_unpinned(snap)
    assert "HOME" not in result["env"]
    assert "PATH" in result["env"]
    assert "DEBUG" in result["env"]


def test_filter_unpinned_returns_all_when_none_pinned(base_snapshot):
    result = filter_unpinned(base_snapshot)
    assert result["env"] == base_snapshot["env"]
