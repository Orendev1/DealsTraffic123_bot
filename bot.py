import os
import json
import logging
from datetime import datetime
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters
import gspread
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message  # ודא שהקובץ parser.py קיים

# --- Telegram & Google Setup ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
SPREADSHEET_NAME = "Telegram Bot Deals"

if not BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN env variable")

if not GOOGLE_CREDS_JSON:
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON env variable")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# --- Google Sheets Auth ---
creds = Credentials.from_service_account_info(json.loads(GOOGLE_CREDS_JSON))
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

# --- Telegram Dispatcher ---
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

def handle_message(update: Update, context):
    try:
        text = update.message.text
        if not text:
            logging.warning("No text in message")
            return

        logging.info(f"📨 Message received: {text[:100]}")

        parsed_deals = parse_affiliate_message(text)
        logging.info(f"🔍 Parsed {len(parsed_deals)} deals")

        for deal in parsed_deals:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                now,
                update.message.chat.title or update.message.chat.username,
                deal.get("GEO", ""),
                deal.get("CPA", ""),
                deal.get("CRG", ""),
                deal.get("CPL", ""),
                deal.get("Funnel", ""),
                deal.get("Source", ""),
                deal.get("Cap", ""),
                deal.get("Deal Type", ""),
                "Negotiation" if deal.get("Negotiation") else "",
                text  # raw message
            ]
            sheet.append_row(row, value_input_option="USER_ENTERED")
            logging.info(f"✅ Deal saved: {deal.get('GEO')}")

    except Exception as e:
        logging.error(f"❌ Error in handle_message: {e}")

# Only handle text messages
dispatcher.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# --- Flask Webhook ---
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update_data = request.get_json(force=True)
        logging.info("🚀 Webhook triggered")
        update = Update.de_json(update_data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        logging.error(f"❌ Error in webhook: {e}")
    return "OK", 200

# --- Health check (for Railway) ---
@app.route('/', methods=['GET'])
def health_check():
    return "Bot is running", 200

# --- Main entry (for local testing if needed) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(port=5000)
