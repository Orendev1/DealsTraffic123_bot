import os
import json
import logging
import sys
from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials
from telegram import Bot

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
def crash_log(msg):
    print(f"❌ CRASH: {msg}", file=sys.stderr)

# --- ENV variables ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
SPREADSHEET_NAME = "Telegram Bot Deals"

if not BOT_TOKEN:
    crash_log("Missing TELEGRAM_BOT_TOKEN")
    raise ValueError("Missing TELEGRAM_BOT_TOKEN")

if not GOOGLE_CREDS_JSON:
    crash_log("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON")
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON")

# --- Google Sheets Auth ---
try:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(json.loads(GOOGLE_CREDS_JSON), scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    logging.info("✅ Connected to Google Sheets.")
except Exception as e:
    crash_log(f"Google Sheets connection failed: {e}")
    raise

# --- Flask App ---
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# --- Webhook route (debug only) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update_data = request.get_json(force=True)
        logging.info("✅ Webhook reached successfully")
        logging.info(f"🧾 Raw data: {json.dumps(update_data, indent=2)[:500]}")
        return "OK", 200
    except Exception as e:
        logging.error(f"❌ Webhook crash: {e}")
        return "ERROR", 500

# --- Health check ---
@app.route('/', methods=['GET'])
def health():
    return "Bot is running", 200

# --- Start Flask ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
