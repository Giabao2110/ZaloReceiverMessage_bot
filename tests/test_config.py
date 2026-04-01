import os

import pytest

from config import load_config


def test_load_config_success(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    monkeypatch.setenv("ZALO_OA_ACCESS_TOKEN", "zalo_token")
    monkeypatch.setenv("POLL_INTERVAL_SECONDS", "5")
    monkeypatch.setenv("MIN_SCAN_DELAY", "2")
    monkeypatch.setenv("MAX_SCAN_DELAY", "6")
    monkeypatch.setenv("SELENIUM_HEADLESS", "true")
    monkeypatch.setenv("KEYWORD_FILE", "foo.json")

    cfg = load_config()

    assert cfg.telegram_token == "abc"
    assert cfg.telegram_chat_id == "123"
    assert cfg.zalo_oa_access_token == "zalo_token"
    assert cfg.poll_interval_seconds == 5
    assert cfg.selenium_headless is True
    assert cfg.keyword_file == "foo.json"


def test_load_config_missing_value(monkeypatch):
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    with pytest.raises(RuntimeError):
        load_config()
