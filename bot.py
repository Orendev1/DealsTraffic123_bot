# bot.py
import os
import json
import logging
from datetime import datetime
from flask import Flask, request

import gspread
from google.oauth2.service_account import Credentials

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from parser import parse_affiliate_message

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- ENV ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Telegram Bot Deals")
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not CREDENTIALS_JSON or not WEBHOOK_URL:
    raise ValueError("Missing required environment variables.")

# --- Google Auth with Scopes ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON), scopes=SCOPES)
gc = gspread.authorize(creds)
spreadsheet = gc.open(SPREADSHEET_NAME)
sheet = spreadsheet.sheet1

# --- Telegram Bot ---
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        print("[DEBUG] Skipping non-text message")
        return

    message = update.message.text
    sender = update.effective_chat.title or update.effective_user.username or str(update.effective_chat.id)
    print(f"[DEBUG] Message from {sender}: {message}")

    deals = parse_affiliate_message(message)
    print("[DEBUG] Parsed deals:", deals)

    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sender,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("CPL", ""),
            deal.get("Deal Type", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            deal.get("CR", ""),
            message
        ]
        print("[DEBUG] Writing row:", row)
        sheet.append_row(row, value_input_option="USER_ENTERED")

# --- Webhook Server ---
flask_app = Flask(__name__)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "OK"

async def set_webhook():
    await bot_app.bot.delete_webhook()
    await bot_app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    logging.info("✅ Webhook set successfully")

# --- Start ---
if __name__ == "__main__":
    import asyncio
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # ✅ זה חייב להיות לפני set_webhook
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=8080)
