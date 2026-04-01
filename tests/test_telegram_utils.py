from unittest.mock import Mock, patch

import pytest

from config import AppConfig
from telegram_utils import send_telegram_message


def make_config():
    return AppConfig(
        telegram_token="token",
        telegram_chat_id="123",
        zalo_oa_access_token="",
        poll_interval_seconds=30,
        chrome_user_data_dir="",
        min_scan_delay=8,
        max_scan_delay=15,
        selenium_headless=False,
        keyword_file="keyword_config.json",
    )


def test_send_telegram_message_missing_config():
    cfg = make_config()
    cfg.telegram_token = ""
    with pytest.raises(ValueError):
        send_telegram_message(cfg, "hi")


def test_send_telegram_message_success():
    cfg = make_config()
    response_mock = Mock()
    response_mock.raise_for_status = Mock()
    response_mock.json.return_value = {"ok": True, "result": {}}

    with patch("telegram_utils.requests.post", return_value=response_mock) as post:
        result = send_telegram_message(cfg, "hi")

    post.assert_called_once()
    assert result["ok"] is True
