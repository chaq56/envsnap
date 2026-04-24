"""Tests for envsnap.restore module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from envsnap.restore import restore_snapshot, generate_export_script


SAMPLE_SNAPSHOT = {
    "APP_ENV": "production",
    "DB_HOST": "db.example.com",
    "SECRET_KEY": "supersecret",
}


@pytest.fixture
def snapshot_dir(tmp_path):
    snap_file = tmp_path / "prod.json"
    snap_file.write_text(json.dumps(SAMPLE_SNAPSHOT))
    return str(tmp_path)


def test_restore_applies_all_vars_to_environ(snapshot_dir):
    restored = restore_snapshot("prod", snapshot_dir)
    for key, value in SAMPLE_SNAPSHOT.items():
        assert os.environ.get(key) == value
    assert restored == SAMPLE_SNAPSHOT


def test_restore_dry_run_does_not_mutate_environ(snapshot_dir):
    # Ensure keys are absent before the call
    for key in SAMPLE_SNAPSHOT:
        os.environ.pop(key, None)

    restored = restore_snapshot("prod", snapshot_dir, dry_run=True)

    assert restored == SAMPLE_SNAPSHOT
    for key in SAMPLE_SNAPSHOT:
        assert key not in os.environ


def test_restore_with_key_filter(snapshot_dir):
    restored = restore_snapshot("prod", snapshot_dir, keys=["APP_ENV", "DB_HOST"])
    assert set(restored.keys()) == {"APP_ENV", "DB_HOST"}
    assert "SECRET_KEY" not in restored


def test_restore_unknown_key_filter_returns_empty(snapshot_dir):
    restored = restore_snapshot("prod", snapshot_dir, keys=["NONEXISTENT"], dry_run=True)
    assert restored == {}


def test_generate_export_script_bash():
    script = generate_export_script({"FOO": "bar", "BAZ": "qux"})
    assert "export BAZ='qux'" in script
    assert "export FOO='bar'" in script


def test_generate_export_script_fish():
    script = generate_export_script({"FOO": "bar"}, shell="fish")
    assert "set -x FOO 'bar'" in script


def test_generate_export_script_powershell():
    script = generate_export_script({"FOO": "bar"}, shell="powershell")
    assert "$env:FOO = 'bar'" in script


def test_generate_export_script_sorted_output():
    script = generate_export_script({"Z_VAR": "z", "A_VAR": "a"})
    lines = script.splitlines()
    assert lines[0] < lines[1]  # A_VAR should come before Z_VAR
