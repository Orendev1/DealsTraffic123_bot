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

# --- ENVIRONMENT ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = "Telegram Bot Deals"
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://your-bot.up.railway.app

if not BOT_TOKEN or not CREDENTIALS_JSON:
    raise ValueError("Missing required environment variables.")

# --- Google Auth with Scopes ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON), scopes=scopes)
gc = gspread.authorize(creds)
spreadsheet = gc.open(SPREADSHEET_NAME)
sheet = spreadsheet.sheet1

# --- Telegram Bot App ---
app = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    sender = update.effective_chat.title or update.effective_user.username or update.effective_chat.id
    deals = parse_affiliate_message(message)

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
        sheet.append_row(row, value_input_option="USER_ENTERED")

# --- Webhook Server ---
flask_app = Flask(__name__)

@app.post("/webhook")
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)
    return "OK"

async def set_webhook():
    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    logging.info("✅ Bot initialized and webhook set!")

# --- Start ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    flask_app.run(host="0.0.0.0", port=8080)
