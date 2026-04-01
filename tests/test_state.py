from pathlib import Path

import pytest

import state


def test_load_last_message_id_not_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(state, "STATE_FILE", tmp_path / "missing.txt")
    assert state.load_last_message_id() is None


def test_save_and_load_last_message_id(tmp_path, monkeypatch):
    file = tmp_path / "state.txt"
    monkeypatch.setattr(state, "STATE_FILE", file)

    state.save_last_message_id("42")
    assert state.load_last_message_id() == "42"


def test_load_last_message_id_invalid_file(tmp_path, monkeypatch):
    file = tmp_path / "state.txt"
    file.write_text("")
    monkeypatch.setattr(state, "STATE_FILE", file)

    assert state.load_last_message_id() is None
