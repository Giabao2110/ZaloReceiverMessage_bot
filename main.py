import os
import time
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

from telegram_utils import send_telegram_message

load_dotenv()

ZALO_OA_ACCESS_TOKEN = os.getenv("ZALO_OA_ACCESS_TOKEN")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))

if not ZALO_OA_ACCESS_TOKEN:
    raise RuntimeError("ZALO_OA_ACCESS_TOKEN must be set in .env")

ZALO_API_URL = "https://openapi.zalo.me/v2.0/oa/message"
STATE_FILE = Path(".last_message_id")


def _load_last_message_id() -> str | None:
    if not STATE_FILE.exists():
        return None
    data = STATE_FILE.read_text(encoding="utf-8").strip()
    return data or None


def _save_last_message_id(msg_id: str) -> None:
    STATE_FILE.write_text(msg_id, encoding="utf-8")


def fetch_recent_zalo_messages(limit: int = 50) -> list[dict]:
    """Gọi API Zalo OA để lấy các tin nhắn gần nhất."""
    headers = {
        "access_token": ZALO_OA_ACCESS_TOKEN,
    }
    params = {
        "offset": 0,
        "limit": limit,
    }

    resp = requests.get(ZALO_API_URL, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    body = resp.json()

    if body.get("error") != 0:
        raise RuntimeError(f"Zalo API error: {body}")

    return body.get("data", [])


def format_zalo_message(message: dict) -> str:
    """Chuẩn hóa nội dung tin nhắn Zalo thành văn bản Telegram-friendly."""
    sender = message.get("sender") or {}
    sender_name = sender.get("name", "Unknown")
    text = message.get("text", "")
    message_id = message.get("message_id")

    text = text or "(No text content)"

    return (
        f"*Zalo message detected*\n"
        f"- *ID*: `{message_id}`\n"
        f"- *Sender*: {sender_name}\n"
        f"- *Content*: {text}"
    )


def main():
    print("Zalo -> Telegram monitor started")
    last_seen = _load_last_message_id()
    if last_seen:
        print(f"Starting from message ID: {last_seen}")

    while True:
        try:
            messages = fetch_recent_zalo_messages(limit=50)
            if not messages:
                print("No messages returned from Zalo.")
            else:
                messages_sorted = sorted(messages, key=lambda m: m.get("message_id", ""))
                new_messages = []

                for msg in messages_sorted:
                    msg_id = str(msg.get("message_id", ""))
                    if not msg_id:
                        continue
                    if last_seen is None or msg_id > last_seen:
                        new_messages.append(msg)

                if new_messages:
                    print(f"Found {len(new_messages)} new message(s)")
                    for msg in new_messages:
                        text = format_zalo_message(msg)
                        send_telegram_message(text)
                        last_seen = str(msg.get("message_id"))
                        _save_last_message_id(last_seen)
                else:
                    print("No new message")

        except Exception as exc:
            print(f"[ERROR] {exc}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
