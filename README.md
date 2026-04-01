# ZaloReceiverMessage_bot

Zalo Web keyword monitor + Telegram alert bot.

## Kiến trúc (Architecture)

- Primary architecture: Selenium-based UI monitoring (`main_selenium.py`).
- Legacy/experimental support: Zalo OA API polling (`main_api.py`).
- Starter script: `main.py` là stub hướng dẫn, không tự chạy logic chính.

### Lý do chọn Selenium làm chính

- Thực tế Zalo không cho phép truy cập nhiều endpoint realtime qua API mở.
- Selenium giám sát giao diện web (chat.zalo.me) phù hợp với yêu cầu giám sát keyword realtime.
- API path giữ cho codebase có tham khảo, bài học và so sánh, tránh xóa hoàn toàn.

## Yêu cầu

- Python 3.10+
- `selenium`, `webdriver-manager`, `requests`, `python-dotenv`
- Chrome bản tương thích với webdriver.

## Cài đặt

1. Clone repo:

   ```bash
   git clone https://github.com/Giabao2110/ZaloReceiverMessage_bot.git
   cd ZaloReceiverMessage_bot/zalo_monitor
   ```

2. Tạo môi trường ảo và cài module:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Tạo và cấu hình `.env` (tham khảo `.env.example`):

   ```ini
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   CHROME_USER_DATA_DIR=C:\Users\<username>\AppData\Local\Google\Chrome\User Data\zalo-monitor-profile
   MIN_SCAN_DELAY=8
   MAX_SCAN_DELAY=15
   SELENIUM_HEADLESS=false
   KEYWORD_FILE=keyword_config.json
   ```

4. Tạo `keyword_config.json`:

   ```json
   {"keywords": ["online"]}
   ```

## Chạy (Primary)

```bash
venv\Scripts\activate
python main_selenium.py
```

## Chạy (Legacy API)

```bash
venv\Scripts\activate
python main_api.py
```

## Giải thích các tệp entrypoint

- `main.py`: stub nằm ở root, góp phần chuyển hướng và giảm nhầm lẫn khi đọc
- `main_selenium.py`: luồng chính được khuyến nghị (Selenium)
- `main_api.py`: luồng polling API (legacy/experimental)

## Kiểm tra sau khi chạy

- `system.log` chứa log Selenium
- Telegram should receive message alerts when keyword appear in Zalo chat

## Lưu ý

- Nếu dùng headless, test ở đầu bằng `false` trước.
- Kiểm tra quyền và đợi Chrome load xong khi tự động mở.
