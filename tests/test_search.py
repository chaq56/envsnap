"""Tests for envsnap.search module."""

import pytest

from envsnap.search import search_snapshot, search_across_snapshots, SEARCH_MODES


@pytest.fixture
def sample_snapshot():
    return {
        "name": "dev",
        "env": {
            "PATH": "/usr/bin:/bin",
            "DATABASE_URL": "postgres://localhost/dev",
            "DEBUG": "true",
            "SECRET_KEY": "abc123",
            "PORT": "8080",
        },
    }


def test_search_modes_constant():
    assert "key" in SEARCH_MODES
    assert "value" in SEARCH_MODES
    assert "both" in SEARCH_MODES


def test_search_by_key_glob(sample_snapshot):
    results = search_snapshot(sample_snapshot, "*URL*", mode="key")
    assert "DATABASE_URL" in results
    assert "PATH" not in results


def test_search_by_value_glob(sample_snapshot):
    results = search_snapshot(sample_snapshot, "*localhost*", mode="value")
    assert "DATABASE_URL" in results
    assert "PORT" not in results


def test_search_mode_both_matches_key_or_value(sample_snapshot):
    results = search_snapshot(sample_snapshot, "*true*", mode="both")
    assert "DEBUG" in results


def test_search_mode_both_matches_key_pattern(sample_snapshot):
    results = search_snapshot(sample_snapshot, "SECRET*", mode="both")
    assert "SECRET_KEY" in results


def test_search_invalid_mode_raises(sample_snapshot):
    with pytest.raises(ValueError, match="Invalid mode"):
        search_snapshot(sample_snapshot, "*", mode="unknown")


def test_search_with_regex(sample_snapshot):
    results = search_snapshot(sample_snapshot, r"^(DEBUG|PORT)$", mode="key", use_regex=True)
    assert "DEBUG" in results
    assert "PORT" in results
    assert "PATH" not in results


def test_search_with_invalid_regex_raises(sample_snapshot):
    import re
    with pytest.raises(re.error):
        search_snapshot(sample_snapshot, "[invalid", use_regex=True)


def test_search_returns_empty_when_no_match(sample_snapshot):
    results = search_snapshot(sample_snapshot, "NONEXISTENT_*", mode="key")
    assert results == {}


def test_search_across_snapshots_groups_by_name():
    snaps = [
        {"name": "dev", "env": {"DEBUG": "true", "PORT": "8080"}},
        {"name": "prod", "env": {"PORT": "443", "WORKERS": "4"}},
    ]
    results = search_across_snapshots(snaps, "PORT", mode="key")
    assert "dev" in results
    assert "prod" in results
    assert results["dev"] == {"PORT": "8080"}
    assert results["prod"] == {"PORT": "443"}


def test_search_across_snapshots_excludes_no_match_snapshots():
    snaps = [
        {"name": "dev", "env": {"DEBUG": "true"}},
        {"name": "prod", "env": {"WORKERS": "4"}},
    ]
    results = search_across_snapshots(snaps, "DEBUG", mode="key")
    assert "dev" in results
    assert "prod" not in results
