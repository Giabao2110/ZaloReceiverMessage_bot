# ZaloReceiverMessage_bot

Zalo Web keyword monitor + Telegram alert bot.

## Mục tiêu

- Giám sát tin nhắn Zalo (chat.zalo.me) bằng Selenium Chrome.
- Tìm keywords trong message text.
- Gửi cảnh báo real-time tới Telegram Bot.

## Yêu cầu

- Python 3.10+
- ruột: selenium, webdriver-manager, requests, python-dotenv
- Chrome cài bản mới tương thích chromedriver.

## Cài đặt

1. Sao chép repository:

   ```bash
   git clone https://github.com/Giabao2110/ZaloReceiverMessage_bot.git
   cd ZaloReceiverMessage_bot/zalo_monitor
   ```

2. Tạo virtual env và cài:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Cấu hình `.env`:

   ```ini
   TELEGRAM_TOKEN=8664235001:AAF9tT6K1SYmxgResktszNsCV42ZTaE5w1o
   TELEGRAM_CHAT_ID=5075385743
   CHROME_USER_DATA_DIR=C:\Users\Gia Bao\AppData\Local\Google\Chrome\User Data\zalo-monitor-profile
   MIN_SCAN_DELAY=8
   MAX_SCAN_DELAY=15
   SELENIUM_HEADLESS=false
   KEYWORD_FILE=keyword_config.json
   ```

4. Cấu hình keyword:

   `keyword_config.json`:
   ```json
   {"keywords":["online"]}
   ```

## Chạy

```bash
venv\Scripts\activate
python zalo_monitor.py
```

- Mở Chrome profile theo `CHROME_USER_DATA_DIR`.
- Lần đầu quét QR login Zalo.
- Chạy sẽ tự dò message; match keyword sẽ gửi Telegram.

## Ghi chú

- Dùng `headless=true` chỉ khi đã hoạt động ổn.
- Đảm bảo `chat_id` và token Telegram đúng.
- Nếu không nhận alert, kiểm tra log `system.log` và content `candidate message`.

## GitHub

- Repo: https://github.com/Giabao2110/ZaloReceiverMessage_bot 
