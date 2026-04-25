"""Tests for envsnap.tag module."""

import pytest

from envsnap.tag import (
    TAG_KEY,
    TagError,
    add_tag,
    filter_snapshots_by_tag,
    list_tags,
    remove_tag,
    tags_index,
)


@pytest.fixture()
def base_snapshot():
    return {"name": "dev", "env": {"HOME": "/home/user"}, TAG_KEY: ["production"]}


def test_add_tag_appends_new_tag(base_snapshot):
    result = add_tag(base_snapshot, "staging")
    assert "staging" in result[TAG_KEY]


def test_add_tag_is_sorted(base_snapshot):
    result = add_tag(base_snapshot, "alpha")
    assert result[TAG_KEY] == sorted(result[TAG_KEY])


def test_add_tag_deduplicates(base_snapshot):
    result = add_tag(base_snapshot, "production")
    assert result[TAG_KEY].count("production") == 1


def test_add_tag_does_not_mutate_original(base_snapshot):
    original_tags = list(base_snapshot[TAG_KEY])
    add_tag(base_snapshot, "new")
    assert base_snapshot[TAG_KEY] == original_tags


def test_add_tag_raises_for_empty_tag(base_snapshot):
    with pytest.raises(TagError, match="empty"):
        add_tag(base_snapshot, "   ")


def test_add_tag_raises_for_tag_with_spaces(base_snapshot):
    with pytest.raises(TagError, match="spaces"):
        add_tag(base_snapshot, "my tag")


def test_remove_tag_removes_existing_tag(base_snapshot):
    result = remove_tag(base_snapshot, "production")
    assert "production" not in result[TAG_KEY]


def test_remove_tag_raises_for_missing_tag(base_snapshot):
    with pytest.raises(TagError, match="not found"):
        remove_tag(base_snapshot, "nonexistent")


def test_remove_tag_does_not_mutate_original(base_snapshot):
    original_tags = list(base_snapshot[TAG_KEY])
    remove_tag(base_snapshot, "production")
    assert base_snapshot[TAG_KEY] == original_tags


def test_list_tags_returns_tags(base_snapshot):
    assert list_tags(base_snapshot) == ["production"]


def test_list_tags_empty_when_no_tags():
    assert list_tags({"name": "empty", "env": {}}) == []


def test_filter_snapshots_by_tag():
    snaps = [
        {"name": "a", TAG_KEY: ["prod"]},
        {"name": "b", TAG_KEY: ["dev"]},
        {"name": "c", TAG_KEY: ["prod", "dev"]},
    ]
    result = filter_snapshots_by_tag(snaps, "prod")
    assert [s["name"] for s in result] == ["a", "c"]


def test_tags_index_builds_correct_mapping():
    snaps = [
        {"name": "snap1", TAG_KEY: ["prod"]},
        {"name": "snap2", TAG_KEY: ["prod", "dev"]},
        {"name": "snap3", TAG_KEY: ["dev"]},
    ]
    index = tags_index(snaps)
    assert set(index["prod"]) == {"snap1", "snap2"}
    assert set(index["dev"]) == {"snap2", "snap3"}


def test_tags_index_empty_snapshots():
    assert tags_index([]) == {}
