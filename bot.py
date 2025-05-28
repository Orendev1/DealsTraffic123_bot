# bot.py
import os
import json
import logging
import gspread
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message
from flask import Flask, request

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- ENVIRONMENT VARIABLES ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # ID only, not full URL
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-bot.up.railway.app

if not BOT_TOKEN or not CREDENTIALS_JSON or not SPREADSHEET_ID:
    raise ValueError("Missing required environment variables.")

# --- Google Auth with proper scopes ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON), scopes=scopes)
gc = gspread.authorize(creds)
spreadsheet = gc.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.sheet1

# --- Telegram Bot App ---
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    sender = update.effective_chat.title or update.effective_user.username or str(update.effective_chat.id)
    deals = parse_affiliate_message(message)

    if not deals:
        logging.info("No deal detected in message.")
        return

    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sender,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message  # raw message for reference
        ]
        logging.info(f"Appending row: {row}")
        sheet.append_row(row, value_input_option="USER_ENTERED")

# --- Flask Webhook Server ---
flask_app = Flask(__name__)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "OK"

async def set_webhook():
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    logging.info("✅ Webhook set!")

# --- Start ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    flask_app.run(host="0.0.0.0", port=8080)
