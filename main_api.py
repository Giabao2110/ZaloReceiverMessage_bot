import logging
import time

from config import load_config
from state import load_last_message_id, save_last_message_id
from telegram_utils import send_telegram_message
from zalo_api import fetch_recent_zalo_messages, format_zalo_message

LOG = logging.getLogger(__name__)


def main():
    config = load_config()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if not config.zalo_oa_access_token:
        LOG.error("ZALO_OA_ACCESS_TOKEN missing, cannot run API poll flow")
        return

    LOG.info("Starting Zalo API polling loop")
    last_seen = load_last_message_id()
    if last_seen:
        LOG.info("Starting from message ID: %s", last_seen)

    while True:
        try:
            messages = fetch_recent_zalo_messages(config.zalo_oa_access_token, limit=50)
            if not messages:
                LOG.info("No messages returned from Zalo API")
            else:
                messages_sorted = sorted(messages, key=lambda m: str(m.get("message_id", "")))
                new_messages = []

                for msg in messages_sorted:
                    msg_id = str(msg.get("message_id", ""))
                    if not msg_id:
                        continue
                    if last_seen is None or msg_id > last_seen:
                        new_messages.append(msg)

                if new_messages:
                    LOG.info("Found %d new message(s)", len(new_messages))
                    for msg in new_messages:
                        try:
                            text = format_zalo_message(msg)
                            send_telegram_message(config, text)
                            last_seen = str(msg.get("message_id", ""))
                            save_last_message_id(last_seen)
                        except Exception:
                            LOG.exception("Failed to handle message %s", msg.get("message_id"))
                else:
                    LOG.debug("No new message")

        except Exception:
            LOG.exception("Error in polling loop")

        time.sleep(config.poll_interval_seconds)


if __name__ == "__main__":
    main()
