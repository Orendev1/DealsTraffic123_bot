import os
import json
import logging
import sys
from flask import Flask
import gspread
from google.oauth2.service_account import Credentials

# -- Logging Setup --
logging.basicConfig(level=logging.INFO)
def crash_log(msg):
    print(f"❌ CRASH: {msg}", file=sys.stderr)

# -- Check ENV --
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
SPREADSHEET_NAME = "Telegram Bot Deals"

if not BOT_TOKEN:
    crash_log("Missing TELEGRAM_BOT_TOKEN")
    raise ValueError("Missing TELEGRAM_BOT_TOKEN")

if not GOOGLE_CREDS_JSON:
    crash_log("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON")
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON")

# -- Google Sheets Auth with Correct Scopes --
try:
    logging.info("🔐 Connecting to Google Sheets with correct scopes...")
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive']

    creds = Credentials.from_service_account_info(json.loads(GOOGLE_CREDS_JSON), scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    logging.info("✅ Google Sheets connection successful.")
except Exception as e:
    crash_log(f"Google Sheets auth failed: {e}")
    raise

# -- Flask App Setup --
app = Flask(__name__)

@app.route('/')
def health():
    logging.info("✅ Health check hit")
    return "Bot is alive", 200

if __name__ == "__main__":
    logging.info("🚀 Starting Flask app...")
    app.run(port=5000)
