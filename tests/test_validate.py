"""Tests for envsnap.validate module."""

import pytest

from envsnap.validate import (
    SnapshotValidationError,
    is_valid_snapshot,
    validate_snapshot,
)


@pytest.fixture
def valid_snapshot():
    return {
        "name": "my-project",
        "timestamp": "2024-01-15T10:30:00",
        "env": {"HOME": "/home/user", "PATH": "/usr/bin"},
    }


def test_validate_passes_for_valid_snapshot(valid_snapshot):
    validate_snapshot(valid_snapshot)  # should not raise


def test_validate_passes_for_empty_env():
    snapshot = {"name": "empty", "timestamp": "2024-01-15T10:30:00", "env": {}}
    validate_snapshot(snapshot)  # should not raise


def test_validate_raises_for_non_dict():
    with pytest.raises(SnapshotValidationError, match="must be a dict"):
        validate_snapshot(["not", "a", "dict"])


def test_validate_raises_for_missing_name():
    with pytest.raises(SnapshotValidationError, match="missing required keys"):
        validate_snapshot({"timestamp": "2024-01-15T10:30:00", "env": {}})


def test_validate_raises_for_missing_timestamp():
    with pytest.raises(SnapshotValidationError, match="missing required keys"):
        validate_snapshot({"name": "test", "env": {}})


def test_validate_raises_for_missing_env():
    with pytest.raises(SnapshotValidationError, match="missing required keys"):
        validate_snapshot({"name": "test", "timestamp": "2024-01-15T10:30:00"})


def test_validate_raises_for_empty_name():
    with pytest.raises(SnapshotValidationError, match="non-empty string"):
        validate_snapshot({"name": "  ", "timestamp": "2024-01-15T10:30:00", "env": {}})


def test_validate_raises_for_non_string_name():
    with pytest.raises(SnapshotValidationError, match="non-empty string"):
        validate_snapshot({"name": 42, "timestamp": "2024-01-15T10:30:00", "env": {}})


def test_validate_raises_for_non_dict_env():
    with pytest.raises(SnapshotValidationError, match="'env' must be a dict"):
        validate_snapshot({"name": "test", "timestamp": "2024-01-15T10:30:00", "env": []})


def test_validate_raises_for_non_string_env_value():
    with pytest.raises(SnapshotValidationError, match="values must be strings"):
        snapshot = {
            "name": "test",
            "timestamp": "2024-01-15T10:30:00",
            "env": {"PORT": 8080},
        }
        validate_snapshot(snapshot)


def test_validate_raises_for_non_string_env_key():
    with pytest.raises(SnapshotValidationError, match="keys must be strings"):
        snapshot = {
            "name": "test",
            "timestamp": "2024-01-15T10:30:00",
            "env": {1: "value"},
        }
        validate_snapshot(snapshot)


def test_is_valid_snapshot_returns_true_for_valid(valid_snapshot):
    assert is_valid_snapshot(valid_snapshot) is True


def test_is_valid_snapshot_returns_false_for_invalid():
    assert is_valid_snapshot({"bad": "data"}) is False


def test_is_valid_snapshot_returns_false_for_none():
    assert is_valid_snapshot(None) is False
