import logging

from config import load_config
from zalo_selenium import load_keywords, run_loop


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    config = load_config()
    keyword_set = load_keywords(config.keyword_file)

    if not keyword_set:
        logging.warning("Keyword list is empty; no alerts will be sent until keywords are provided.")

    logging.info("Starting Selenium monitor with %d keywords", len(keyword_set))

    try:
        run_loop(config, keyword_set)
    except Exception:
        logging.exception("Fatal error in Selenium monitor")


if __name__ == "__main__":
    main()
