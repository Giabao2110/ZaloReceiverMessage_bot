import json
import logging
import os
import platform
import random
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple

import requests
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from telegram_utils import send_telegram_message
from config import AppConfig

LOG = logging.getLogger(__name__)


def get_default_profile_dir() -> str:
    if platform.system() == "Windows":
        return str(Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data/zalo-monitor-profile")
    if platform.system() == "Darwin":
        return str(Path.home() / "Library/Application Support/Google/Chrome/zalo-monitor-profile")
    return str(Path.home() / ".config/google-chrome/zalo-monitor-profile")


def load_keywords(keyword_file: str) -> Set[str]:
    path = Path(keyword_file)
    if not path.exists():
        LOG.warning("Keyword file %s not found. No keywords loaded.", path)
        return set()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        keywords = data.get("keywords", [])
        return {kw.strip().lower() for kw in keywords if isinstance(kw, str) and kw.strip()}
    except json.JSONDecodeError as exc:
        LOG.error("Keyword file parse error: %s", exc)
        return set()


def build_webdriver(cfg: AppConfig):
    options = Options()
    user_data = cfg.chrome_user_data_dir or get_default_profile_dir()
    options.add_argument(f"--user-data-dir={user_data}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")

    if cfg.selenium_headless:
        LOG.info("Selenium headless mode enabled")
        options.add_argument("--headless=new")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as exc:
        LOG.exception("Failed to start Chrome WebDriver")
        raise


def ensure_logged_in(driver) -> bool:
    LOG.info("Opening https://chat.zalo.me/ for login")
    driver.get("https://chat.zalo.me/")
    time.sleep(2)

    timeout = time.time() + 180
    while time.time() < timeout:
        current = driver.current_url.lower()
        if "chat.zalo.me" in current and "login" not in current:
            LOG.info("Zalo Web login detected")
            return True
        time.sleep(2)

    LOG.warning("Login timeout. Please complete login manually and press Enter.")
    input("Login done? Press Enter to continue...")
    return True


def collect_recent_messages(driver) -> List[Tuple[str, str, str]]:
    results = []

    try:
        active_msgs = driver.find_elements(By.CSS_SELECTOR, "div[class*='msg'], div[class*='Message'], div[class*='bubble']")
        for i, el in enumerate(active_msgs[-50:], start=1):
            try:
                txt = el.text.strip()
                if txt:
                    key = f"active-{i}-{hash(txt)}"
                    results.append((key, "[active chat]", txt))
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        if results:
            LOG.info("Read %d messages from active chat", len(results))
            return results
    except Exception as exc:
        LOG.debug("Active chat parse issue: %s", exc)

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

                if snippet:
                    mid = el.get_attribute("data-id") or el.get_attribute("id") or f"{hash(sender + snippet)}"
                    results.append((mid, sender or "[chat list]", snippet))
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        if results:
            LOG.info("Read %d messages from chat list", len(results))
    except Exception as exc:
        LOG.exception("Failed to parse chat list")

    return results


def normalize_markdown(text: str) -> str:
    escape_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '>', '#', '+', '-', '.', '!']
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def run_loop(cfg: AppConfig, keywords: Set[str]):
    visited = set()
    driver = build_webdriver(cfg)

    try:
        ensure_logged_in(driver)

        while True:
            try:
                driver.refresh()
                time.sleep(2 + random.uniform(0.5, 1.5))

                messages = collect_recent_messages(driver)
                LOG.info("Candidate messages fetched: %d", len(messages))

                for mid, sender, snippet in messages:
                    key = f"{mid}|{snippet[:128]}"
                    if key in visited:
                        continue

                    visited.add(key)

                    for kw in keywords:
                        if kw in snippet.lower():
                            sanitized = normalize_markdown(snippet)
                            result = send_telegram_message(
                                cfg,
                                f"🚨 *Zalo Keyword Alert!*\n*Keyword:* `{normalize_markdown(kw)}`\n*Sender:* {normalize_markdown(sender)}\n*Message:* {sanitized}",
                                parse_mode="MarkdownV2",
                            )
                            LOG.info("Keyword match sent to Telegram: %s | response: %s", kw, result)
                            break

                if len(visited) > 10000:
                    visited = set(list(visited)[-5000:])

            except (WebDriverException, requests.RequestException) as exc:
                LOG.exception("Temporary Selenium/request error")
                time.sleep(random.uniform(10, 20))

            delay = random.uniform(cfg.min_scan_delay, cfg.max_scan_delay)
            LOG.info("Sleeping for %.1f seconds", delay)
            time.sleep(delay)

    finally:
        LOG.info("Closing WebDriver")
        driver.quit()
