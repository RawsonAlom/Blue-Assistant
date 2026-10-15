"""Tests for BLUE's SQLite memory store."""

import pytest

from memory.store import MemoryStore


def make_store(tmp_path):
    return MemoryStore(tmp_path / "blue-test.sqlite3")


def test_store_creates_database(tmp_path):
    db_path = tmp_path / "nested" / "blue.sqlite3"

    store = MemoryStore(db_path)

    assert db_path.is_file()
    assert store.get_history("session") == []


def test_conversation_history_persists_in_order(tmp_path):
    db_path = tmp_path / "blue.sqlite3"
    store = MemoryStore(db_path)

    store.add_message("session-1", "user", "Hello")
    store.add_message("session-1", "assistant", "Hello back")

    # A separate store instance proves that data is persisted.
    reopened = MemoryStore(db_path)
    history = reopened.get_history("session-1")

    assert [message.role for message in history] == [
        "user",
        "assistant",
    ]
    assert [message.content for message in history] == [
        "Hello",
        "Hello back",
    ]


def test_history_limit_returns_latest_messages_in_order(tmp_path):
    store = make_store(tmp_path)

    for number in range(4):
        store.add_message("session-1", "user", f"Message {number}")

    history = store.get_history("session-1", limit=2)

    assert [message.content for message in history] == [
        "Message 2",
        "Message 3",
    ]


def test_history_is_isolated_by_session(tmp_path):
    store = make_store(tmp_path)

    store.add_message("session-A", "user", "Private to A")
    store.add_message("session-B", "user", "Private to B")

    assert [m.content for m in store.get_history("session-A")] == [
        "Private to A"
    ]


@pytest.mark.parametrize("content", ["", "   "])
def test_message_rejects_empty_content(tmp_path, content):
    store = make_store(tmp_path)

    with pytest.raises(ValueError):
        store.add_message("session", "user", content)


def test_message_rejects_unknown_role(tmp_path):
    store = make_store(tmp_path)

    with pytest.raises(ValueError):
        store.add_message("session", "tool", "Unexpected role")  # type: ignore[arg-type]


def test_memory_can_be_saved_and_listed(tmp_path):
    store = make_store(tmp_path)

    memory = store.add_memory("Prefers concise answers")
    records = store.list_memories()

    assert memory.id > 0
    assert memory.content == "Prefers concise answers"
    assert len(records) == 1
    assert records[0].id == memory.id


def test_memory_search_finds_matching_substring(tmp_path):
    store = make_store(tmp_path)
    store.add_memory("Prefers concise answers")
    store.add_memory("Likes dark themes")

    results = store.search_memories("CONCISE")

    assert len(results) == 1
    assert results[0].content == "Prefers concise answers"


def test_memory_can_be_updated_and_deleted(tmp_path):
    store = make_store(tmp_path)
    memory = store.add_memory("Old preference")

    updated = store.update_memory(memory.id, "Updated preference")

    assert updated is not None
    assert updated.content == "Updated preference"

    assert store.delete_memory(memory.id) is True
    assert store.list_memories() == []
    assert store.delete_memory(memory.id) is False


def test_missing_memory_update_returns_none(tmp_path):
    store = make_store(tmp_path)

    assert store.update_memory(999, "Not found") is None


def test_search_empty_query_returns_no_results(tmp_path):
    store = make_store(tmp_path)
    store.add_memory("Keep this memory")

    assert store.search_memories("   ") == []


def test_memory_content_is_parameterized(tmp_path):
    store = make_store(tmp_path)
    store.add_memory("Normal preference")

    # Search input is treated as literal data, not SQL code.
    assert store.search_memories("' OR 1=1 --") == []


def test_invalid_limit_is_rejected(tmp_path):
    store = make_store(tmp_path)

    with pytest.raises(ValueError):
        store.list_memories(limit=0)


def test_empty_memory_is_rejected(tmp_path):
    store = make_store(tmp_path)

    with pytest.raises(ValueError):
        store.add_memory("   ")
