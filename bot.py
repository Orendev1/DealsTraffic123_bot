# bot.py
import os
import json
import logging
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message
from datetime import datetime
from flask import Flask, request

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- ENV ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = "Telegram Bot Deals"
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-bot.up.railway.app

if not BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment.")

if not CREDENTIALS_JSON:
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON in environment.")

# --- Google Auth ---
creds_dict = json.loads(CREDENTIALS_JSON)
creds = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(creds)
sh = gc.open(SPREADSHEET_NAME)
worksheet = sh.sheet1

# --- Flask Webhook ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot running"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

# --- Telegram Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    logging.info("\U0001F4AC Incoming message:\n\n%s", message)

    try:
        deals = parse_affiliate_message(message)
    except Exception as e:
        logging.exception("Failed to parse message")
        return

    if not deals:
        logging.info("No deals parsed from message.")
        return

    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update.message.chat.title or update.message.chat.username or update.message.chat.id,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message
        ]
        worksheet.append_row(row)
        logging.info("✅ Deal saved: %s", row)

# --- Telegram Bot Init ---
application = ApplicationBuilder().token(BOT_TOKEN).build()
bot = application.bot
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

async def main():
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    logging.info("\u2705 Bot initialized and webhook set!")

import asyncio
asyncio.run(main())

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
