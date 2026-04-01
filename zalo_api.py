import logging
from typing import Any, Dict, List

import requests

LOG = logging.getLogger(__name__)


def fetch_recent_zalo_messages(access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Call Zalo OA API and return list of messages."""
    if not access_token:
        raise ValueError("ZALO_OA_ACCESS_TOKEN is required")

    url = "https://openapi.zalo.me/v2.0/oa/message"
    headers = {"access_token": access_token}
    params = {"offset": 0, "limit": limit}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as exc:
        LOG.exception("Zalo API request failed")
        raise
    except ValueError as exc:
        LOG.exception("Failed to parse JSON response from Zalo API")
        raise

    if not isinstance(body, dict):
        raise RuntimeError("Unexpected Zalo API response format")

    if body.get("error") != 0:
        message = body.get("message", "Unknown error")
        raise RuntimeError(f"Zalo API returned an error: {message}")

    data = body.get("data")
    if not isinstance(data, list):
        raise RuntimeError("Zalo API response data is missing or malformed")

    return data


def format_zalo_message(message: Dict[str, Any]) -> str:
    sender = message.get("sender") or {}
    sender_name = sender.get("name", "Unknown")
    text = message.get("text") or "(No text content)"
    message_id = message.get("message_id", "N/A")

    return (
        f"*Zalo message detected*\n"
        f"- *ID*: `{message_id}`\n"
        f"- *Sender*: {sender_name}\n"
        f"- *Content*: {text}"
    )
