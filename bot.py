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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # לדוגמה: https://your-bot.up.railway.app

if not BOT_TOKEN or not CREDENTIALS_JSON:
    raise ValueError("Missing required environment variables.")

# --- Google Auth ---
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON))
gc = gspread.authorize(creds)
spreadsheet = gc.open(SPREADSHEET_NAME)
sheet = spreadsheet.sheet1

# --- Flask App (Webhook server) ---
flask_app = Flask(__name__)

# --- Telegram App ---
application = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    sender = update.effective_chat.title or update.effective_user.username or str(update.effective_chat.id)
    logging.info(f"💬 Incoming message from {sender}: {message}")
    
    deals = parse_affiliate_message(message)

    if not deals:
        logging.info("🔍 No relevant deals parsed.")
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
            message  # Raw message for reference
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logging.info(f"✅ Row added: {row}")

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    logging.info("📥 Webhook triggered!")
    return "OK"

async def set_webhook():
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    logging.info("✅ Bot initialized and webhook set!")

# --- Start Server ---
if __name__ == "__main__":
    import asyncio
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=8080)
