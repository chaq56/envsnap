"""Tests for envsnap.diff module."""

import pytest

from envsnap.diff import diff_snapshots, format_diff


@pytest.fixture()
def base_snapshot() -> dict[str, str]:
    return {
        "HOME": "/home/alice",
        "PATH": "/usr/bin:/bin",
        "OLD_VAR": "to_be_removed",
        "SHARED": "same_value",
    }


@pytest.fixture()
def target_snapshot() -> dict[str, str]:
    return {
        "HOME": "/home/alice",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "NEW_VAR": "brand_new",
        "SHARED": "same_value",
    }


def test_diff_detects_added_keys(base_snapshot, target_snapshot):
    result = diff_snapshots(base_snapshot, target_snapshot)
    assert result["added"] == {"NEW_VAR": "brand_new"}


def test_diff_detects_removed_keys(base_snapshot, target_snapshot):
    result = diff_snapshots(base_snapshot, target_snapshot)
    assert result["removed"] == {"OLD_VAR": "to_be_removed"}


def test_diff_detects_changed_keys(base_snapshot, target_snapshot):
    result = diff_snapshots(base_snapshot, target_snapshot)
    assert result["changed"] == {
        "PATH": ("/usr/bin:/bin", "/usr/local/bin:/usr/bin:/bin")
    }


def test_diff_detects_unchanged_keys(base_snapshot, target_snapshot):
    result = diff_snapshots(base_snapshot, target_snapshot)
    assert "HOME" in result["unchanged"]
    assert "SHARED" in result["unchanged"]


def test_diff_identical_snapshots():
    snap = {"FOO": "bar", "BAZ": "qux"}
    result = diff_snapshots(snap, snap)
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == snap


def test_diff_empty_snapshots():
    result = diff_snapshots({}, {})
    assert result == {"added": {}, "removed": {}, "changed": {}, "unchanged": {}}


def test_format_diff_contains_added_prefix(base_snapshot, target_snapshot):
    diff = diff_snapshots(base_snapshot, target_snapshot)
    output = format_diff(diff)
    assert "+ NEW_VAR=brand_new" in output


def test_format_diff_contains_removed_prefix(base_snapshot, target_snapshot):
    diff = diff_snapshots(base_snapshot, target_snapshot)
    output = format_diff(diff)
    assert "- OLD_VAR=to_be_removed" in output


def test_format_diff_contains_changed_prefix(base_snapshot, target_snapshot):
    diff = diff_snapshots(base_snapshot, target_snapshot)
    output = format_diff(diff)
    assert "~ PATH" in output


def test_format_diff_no_differences_message():
    snap = {"X": "1"}
    diff = diff_snapshots(snap, snap)
    assert format_diff(diff) == "No differences found."


def test_format_diff_show_unchanged(base_snapshot, target_snapshot):
    diff = diff_snapshots(base_snapshot, target_snapshot)
    output = format_diff(diff, show_unchanged=True)
    assert "  HOME=/home/alice" in output
