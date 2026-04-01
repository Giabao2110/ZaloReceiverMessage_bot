import os
import json
import time
import random
import logging
import platform
from pathlib import Path
from typing import Set, Tuple

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

from telegram_utils import send_telegram_message

load_dotenv()

LOG_PATH = Path("system.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH, encoding="utf-8")],
)


def get_default_profile_dir() -> str:
    if platform.system() == "Windows":
        return os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data\\zalo-monitor-profile")
    if platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome/zalo-monitor-profile")
    return os.path.expanduser("~/.config/google-chrome/zalo-monitor-profile")


def load_config():
    return {
        "user_data_dir": os.getenv("CHROME_USER_DATA_DIR", get_default_profile_dir()),
        "min_delay": float(os.getenv("MIN_SCAN_DELAY", "8")),
        "max_delay": float(os.getenv("MAX_SCAN_DELAY", "15")),
        "headless": os.getenv("SELENIUM_HEADLESS", "false").lower() in ("1", "true", "yes"),
        "keyword_file": os.getenv("KEYWORD_FILE", "keyword_config.json"),
    }


def load_keywords(keyword_file: str) -> Set[str]:
    p = Path(keyword_file)
    if not p.exists():
        logging.warning("Không tìm thấy %s. Dùng tập từ khóa rỗng.", keyword_file)
        return set()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        texts = data.get("keywords", [])
        return {str(k).strip().lower() for k in texts if isinstance(k, str) and k.strip()}
    except json.JSONDecodeError as e:
        logging.error("Lỗi decode JSON từ %s: %s", keyword_file, e)
        return set()


def build_webdriver(cfg):
    options = Options()
    options.add_argument(f"--user-data-dir={cfg['user_data_dir']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    if cfg["headless"]:
        logging.info("Chạy headless")
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def ensure_logged_in(driver):
    logging.info("Mở https://chat.zalo.me để login (quét QR nếu cần)")
    driver.get("https://chat.zalo.me/")
    time.sleep(2)

    timeout = time.time() + 180
    while time.time() < timeout:
        current = driver.current_url.lower()
        if "chat.zalo.me" in current and "login" not in current:
            logging.info("Đã đăng nhập Zalo Web.")
            return True
        time.sleep(2)

    logging.warning("Hết thời gian chờ login. Vui lòng quét QR và nhấn Enter")
    input("Đã login xong chưa? Nhấn Enter tiếp tục...")
    return True


def collect_recent_messages(driver):
    results = []
    tried = []

    # 1) khám phá nội dung trò chuyện hiện tại (message bubble)
    try:
        active_msgs = driver.find_elements(By.CSS_SELECTOR, "div[class*='msg'] , div[class*='Message'] , div[class*='bubble']")
        for i, el in enumerate(active_msgs[-50:], start=1):
            try:
                txt = el.text.strip()
                if txt:
                    key = f"active-{i}-{hash(txt)}"
                    results.append((key, "[active chat]", txt))
            except (StaleElementReferenceException, NoSuchElementException):
                continue
        if results:
            logging.info("Lấy %d message từ conversation hiện tại", len(results))
            return results
    except Exception as e:
        logging.debug("Không tìm thấy conversation zalo hiện tại: %s", e)

    # 2) fallback: chat list left panel
    try:
        message_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'chat-item') or contains(@class,'conversation-item') or contains(@class,'chatListItem') or contains(@class,'chatItem')]")
        for el in message_elements[:30]:
            try:
                snippet = ""
                sender = ""
                try:
                    snippet = el.find_element(By.XPATH, ".//div[contains(@class,'last-message') or contains(@class,'snippet') or .//span[contains(@class,'message')]]").text.strip()
                except (NoSuchElementException, StaleElementReferenceException):
                    pass

                try:
                    sender = el.find_element(By.XPATH, ".//div[contains(@class,'title') or contains(@class,'name') or contains(@class,'chat-title') or contains(@class,'username')]").text.strip()
                except (NoSuchElementException, StaleElementReferenceException):
                    pass

                mid = el.get_attribute("data-id") or el.get_attribute("id") or f"{hash(sender + snippet)}"
                if snippet:
                    results.append((mid, sender or "[chat list]", snippet))
            except (StaleElementReferenceException, NoSuchElementException):
                continue
    except Exception as e:
        logging.error("Lỗi khi đọc DOM chat list: %s", e)

    if results:
        logging.info("Lấy %d message từ chat list", len(results))
    return results


def normalize_markdown(text: str) -> str:
    escape_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '>', '#', '+', '-', '.', '!']
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def run_loop(cfg, keywords):
    visited = set()
    driver = build_webdriver(cfg)

    try:
        ensure_logged_in(driver)

        while True:
            try:
                driver.refresh()
                time.sleep(2 + random.uniform(0.5, 1.5))

                messages = collect_recent_messages(driver)
                logging.info("Found %d candidate messages from DOM.", len(messages))
                if not messages:
                    logging.info("Chưa có tin nhắn mới trong cuộc trò chuyện hiện tại.")

                for mid, sender, snippet in messages:
                    logging.debug("Candidate message captured: sender=%s snippet=%s", sender, snippet[:120])
                    key = f"{mid}|{snippet[:128]}"
                    if key in visited:
                        continue

                    visited.add(key)
                    for kw in keywords:
                        if kw in snippet.lower():
                            sanitized = normalize_markdown(snippet)
                            kw_safe = normalize_markdown(kw)
                            send_telegram_message(
                                f"🚨 *Zalo Keyword Alert!*\n*Keyword:* `{kw_safe}`\n*Sender:* {normalize_markdown(sender)}\n*Message:* {sanitized}",
                                parse_mode="MarkdownV2",
                            )
                            logging.info("Gửi alert với keyword %s: %s", kw, snippet[:100])
                            break

                if len(visited) > 10000:
                    visited = set(list(visited)[-5000:])

            except (WebDriverException, requests.RequestException) as e:
                logging.exception("Lỗi tạm thời, retry: %s", e)
                time.sleep(random.uniform(10, 20))

            delay = random.uniform(cfg["min_delay"], cfg["max_delay"])
            logging.info("Sleep %s giây.", round(delay, 2))
            time.sleep(delay)

    finally:
        logging.info("Đóng driver.")
        driver.quit()


if __name__ == "__main__":
    config = load_config()
    keyword_set = load_keywords(config["keyword_file"])
    if not keyword_set:
        logging.warning("Danh sách keyword trống, không cảnh báo gì.")
    logging.info("Khởi động với %d keyword", len(keyword_set))
    run_loop(config, keyword_set)
