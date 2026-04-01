import logging
from typing import Any, Dict

import requests

from config import AppConfig

LOG = logging.getLogger(__name__)


def send_telegram_message(config: AppConfig, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
    """Send a Telegram message using bot token from config."""
    if not config.telegram_token or not config.telegram_chat_id:
        raise ValueError("Telegram token or chat ID is missing")

    url = f"https://api.telegram.org/bot{config.telegram_token}/sendMessage"
    payload = {
        "chat_id": config.telegram_chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as exc:
        LOG.exception("Failed to send Telegram message")
        raise
    except ValueError:
        LOG.exception("Malformed response from Telegram gateway")
        raise
