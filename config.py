import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

LOG = logging.getLogger(__name__)

@dataclass
class AppConfig:
    telegram_token: str
    telegram_chat_id: str
    zalo_oa_access_token: str
    poll_interval_seconds: int
    chrome_user_data_dir: str
    min_scan_delay: float
    max_scan_delay: float
    selenium_headless: bool
    keyword_file: str


def load_config() -> AppConfig:
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    zalo_oa_access_token = os.getenv("ZALO_OA_ACCESS_TOKEN", "")

    if not telegram_token or not telegram_chat_id:
        LOG.error("TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in .env")
        raise RuntimeError("TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set")

    if not zalo_oa_access_token:
        LOG.warning("ZALO_OA_ACCESS_TOKEN not set. API polling path may fail unless it is set.")

    try:
        poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
    except ValueError:
        poll_interval = 30

    chrome_user_data_dir = os.getenv("CHROME_USER_DATA_DIR", "")
    min_delay = float(os.getenv("MIN_SCAN_DELAY", "8"))
    max_delay = float(os.getenv("MAX_SCAN_DELAY", "15"))
    selenium_headless = os.getenv("SELENIUM_HEADLESS", "false").strip().lower() in ("1", "true", "yes")
    keyword_file = os.getenv("KEYWORD_FILE", "keyword_config.json")

    return AppConfig(
        telegram_token=telegram_token,
        telegram_chat_id=telegram_chat_id,
        zalo_oa_access_token=zalo_oa_access_token,
        poll_interval_seconds=poll_interval,
        chrome_user_data_dir=chrome_user_data_dir,
        min_scan_delay=min_delay,
        max_scan_delay=max_delay,
        selenium_headless=selenium_headless,
        keyword_file=keyword_file,
    )
