"""Tests for envsnap.merge module."""

import pytest
from envsnap.merge import merge_snapshots, MergeConflictError, MERGE_STRATEGIES


@pytest.fixture
def snap_a():
    return {"name": "snap_a", "timestamp": "2024-01-01T00:00:00", "env": {"FOO": "1", "SHARED": "from_a"}}


@pytest.fixture
def snap_b():
    return {"name": "snap_b", "timestamp": "2024-01-02T00:00:00", "env": {"BAR": "2", "SHARED": "from_b"}}


@pytest.fixture
def snap_c():
    return {"name": "snap_c", "timestamp": "2024-01-03T00:00:00", "env": {"BAZ": "3", "SHARED": "from_c"}}


def test_merge_strategies_constant():
    assert "last_wins" in MERGE_STRATEGIES
    assert "first_wins" in MERGE_STRATEGIES
    assert "error_on_conflict" in MERGE_STRATEGIES


def test_merge_requires_at_least_two_snapshots(snap_a):
    with pytest.raises(ValueError, match="At least two"):
        merge_snapshots([snap_a])


def test_merge_raises_on_unknown_strategy(snap_a, snap_b):
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge_snapshots([snap_a, snap_b], strategy="invalid")


def test_merge_last_wins_resolves_conflict(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b], strategy="last_wins")
    assert result["env"]["SHARED"] == "from_b"


def test_merge_first_wins_resolves_conflict(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b], strategy="first_wins")
    assert result["env"]["SHARED"] == "from_a"


def test_merge_error_on_conflict_raises(snap_a, snap_b):
    with pytest.raises(MergeConflictError) as exc_info:
        merge_snapshots([snap_a, snap_b], strategy="error_on_conflict")
    assert exc_info.value.key == "SHARED"


def test_merge_combines_unique_keys(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b])
    assert "FOO" in result["env"]
    assert "BAR" in result["env"]


def test_merge_records_source_names(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b])
    assert result["sources"] == ["snap_a", "snap_b"]


def test_merge_custom_label(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b], label="my_merge")
    assert result["name"] == "my_merge"


def test_merge_default_label_contains_source_names(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b])
    assert "snap_a" in result["name"]
    assert "snap_b" in result["name"]


def test_merge_three_snapshots(snap_a, snap_b, snap_c):
    result = merge_snapshots([snap_a, snap_b, snap_c], strategy="last_wins")
    assert result["env"]["SHARED"] == "from_c"
    assert result["env"]["FOO"] == "1"
    assert result["env"]["BAR"] == "2"
    assert result["env"]["BAZ"] == "3"


def test_merge_conflict_tracker_populated(snap_a, snap_b):
    result = merge_snapshots([snap_a, snap_b], strategy="last_wins")
    assert "SHARED" in result["conflicts"]


def test_merge_no_conflicts_when_disjoint():
    s1 = {"name": "s1", "env": {"A": "1"}}
    s2 = {"name": "s2", "env": {"B": "2"}}
    result = merge_snapshots([s1, s2])
    assert result["conflicts"] == {}
