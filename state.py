from pathlib import Path
from typing import Optional
import logging

LOG = logging.getLogger(__name__)
STATE_FILE = Path(".last_message_id")


def load_last_message_id() -> Optional[str]:
    if not STATE_FILE.exists():
        return None

    try:
        value = STATE_FILE.read_text(encoding="utf-8").strip()
        return value or None
    except Exception as exc:
        LOG.error("Failed to load last message id: %s", exc)
        return None


def save_last_message_id(msg_id: str) -> None:
    try:
        STATE_FILE.write_text(str(msg_id), encoding="utf-8")
    except Exception as exc:
        LOG.error("Failed to save last message id: %s", exc)
