import pytest
from unittest.mock import Mock, patch

from zalo_api import fetch_recent_zalo_messages, format_zalo_message


def test_fetch_recent_zalo_messages_no_token():
    with pytest.raises(ValueError):
        fetch_recent_zalo_messages("")


def test_fetch_recent_zalo_messages_error_in_response():
    fake = Mock()
    fake.raise_for_status = Mock()
    fake.json.return_value = {"error": 1, "message": "bad"}

    with patch("zalo_api.requests.get", return_value=fake):
        with pytest.raises(RuntimeError, match="Zalo API returned an error"):
            fetch_recent_zalo_messages("token")


def test_fetch_recent_zalo_messages_success():
    fake = Mock()
    fake.raise_for_status = Mock()
    fake.json.return_value = {"error": 0, "data": [{"message_id": "1", "sender": {"name": "A"}, "text": "hi"}]}

    with patch("zalo_api.requests.get", return_value=fake):
        res = fetch_recent_zalo_messages("token")
    assert len(res) == 1


def test_format_zalo_message_defaults():
    fmt = format_zalo_message({})
    assert "Unknown" in fmt
    assert "(No text content)" in fmt
