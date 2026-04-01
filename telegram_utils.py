import os
import requests

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_telegram_message(text: str, parse_mode: str = "Markdown") -> dict:
    """Gửi tin nhắn tới Telegram qua bot."""
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    r = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=15)
    r.raise_for_status()
    return r.json()
