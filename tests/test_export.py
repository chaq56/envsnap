"""Tests for envsnap.export module."""

import json
import pytest

from envsnap.export import export_snapshot, SUPPORTED_FORMATS


@pytest.fixture
def sample_snapshot():
    return {
        "APP_ENV": "production",
        "DB_HOST": "localhost",
        "DB_PASS": 'p@ss"word',
        "SECRET_KEY": "abc123",
    }


def test_supported_formats_constant():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS


def test_export_unsupported_format_raises(sample_snapshot):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_snapshot(sample_snapshot, fmt="yaml")


def test_export_dotenv_format(sample_snapshot):
    result = export_snapshot(sample_snapshot, fmt="dotenv")
    assert "APP_ENV=\"production\"" in result
    assert "DB_HOST=\"localhost\"" in result


def test_export_dotenv_escapes_double_quotes(sample_snapshot):
    result = export_snapshot(sample_snapshot, fmt="dotenv")
    # Inner double-quote in 'p@ss"word' must be escaped
    assert '\\"' in result


def test_export_shell_format(sample_snapshot):
    result = export_snapshot(sample_snapshot, fmt="shell")
    assert "export APP_ENV=\"production\"" in result
    assert "export SECRET_KEY=\"abc123\"" in result


def test_export_json_format(sample_snapshot):
    result = export_snapshot(sample_snapshot, fmt="json")
    parsed = json.loads(result)
    assert parsed["APP_ENV"] == "production"
    assert parsed["DB_PASS"] == 'p@ss"word'


def test_export_with_prefix_filter(sample_snapshot):
    result = export_snapshot(sample_snapshot, fmt="dotenv", prefix="DB_")
    assert "DB_HOST" in result
    assert "DB_PASS" in result
    assert "APP_ENV" not in result
    assert "SECRET_KEY" not in result


def test_export_prefix_no_match_returns_empty(sample_snapshot):
    result = export_snapshot(sample_snapshot, fmt="dotenv", prefix="NOMATCH_")
    assert result == ""


def test_export_empty_snapshot():
    result = export_snapshot({}, fmt="dotenv")
    assert result == ""


def test_export_json_empty_snapshot():
    result = export_snapshot({}, fmt="json")
    assert json.loads(result) == {}


def test_export_dotenv_sorted_keys():
    snap = {"Z_VAR": "z", "A_VAR": "a", "M_VAR": "m"}
    result = export_snapshot(snap, fmt="dotenv")
    lines = result.splitlines()
    keys = [line.split("=")[0] for line in lines]
    assert keys == sorted(keys)
