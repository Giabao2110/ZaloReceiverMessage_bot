"""Entrypoint cho Zalo monitor.

Theo quyết định kiến trúc (Phase: API-vs-Selenium), đường chính là Selenium (main_selenium.py).
API polling (main_api.py) vẫn giữ như legacy reference.
"""

import sys

print("=== ZaloReceiverMessage_bot: primary flow = Selenium (main_selenium.py) ===")
print("Use `python main_selenium.py` to run the recommended path.")
print("Optional legacy API path: `python main_api.py`.")

if __name__ == '__main__':
    print("Run command explicitly; this stub does not execute a monitoring loop.")
    print("Exiting.")
    sys.exit(0)
