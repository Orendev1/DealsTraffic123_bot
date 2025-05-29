import os
import json
import logging
import sys
from flask import Flask, request
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from parser import parse_affiliate_message  # ודא שהקובץ הזה קיים

# --- Logging ---
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

# --- Message handling manually via Flask ---
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, bot)
        message = update.effective_message

        if not message or not message.text:
            logging.warning("📭 No valid message text found.")
            return "NO TEXT", 200

        logging.info(f"📩 Message received: {message.text[:100]}")
        parsed_deals = parse_affiliate_message(message.text)
        logging.info(f"🔍 Parsed {len(parsed_deals)} deals")

        for deal in parsed_deals:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                now,
                message.chat.title or message.chat.username or "Unknown",
                deal.get("GEO", ""),
                deal.get("CPA", ""),
                deal.get("CRG", ""),
                deal.get("CPL", ""),
                deal.get("Funnel", ""),
                deal.get("Source", ""),
                deal.get("Cap", ""),
                deal.get("Deal Type", ""),
                "Negotiation" if deal.get("Negotiation") else "",
                message.text
            ]
            sheet.append_row(row, value_input_option="USER_ENTERED")
            logging.info(f"✅ Deal saved: {deal.get('GEO')}")

        return "OK", 200

    except Exception as e:
        logging.error(f"❌ Webhook error: {e}")
        return "ERROR", 500

# --- Health Check ---
@app.route('/', methods=['GET'])
def health():
    return "Bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
