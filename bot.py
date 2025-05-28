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
logger = logging.getLogger(__name__)

# --- ENV ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = "Telegram Bot Deals"
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # example: https://your-bot.up.railway.app

if not BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment.")
if not CREDENTIALS_JSON:
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON in environment.")

# --- Google Auth ---
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON))
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# --- Flask for webhook ---
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("Webhook triggered!")
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.process_update(update))
    return "OK"

# --- Message Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = update.effective_user.username or "Unknown"
    chat_title = update.effective_chat.title or username
    logger.info("💬 Incoming message:\n%s", message)

    deals = parse_affiliate_message(message)
    if not deals:
        logger.info("⚠️ No relevant deals found in message.")
        return

    for deal in deals:
        row = [
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            chat_title,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message.replace('\n', ' ')[:1000]  # raw message snippet
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info("✅ Deal saved: %s", row)

# --- Telegram Bot Setup ---
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Set webhook ---
async def set_webhook():
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    logger.info("✅ Bot initialized and webhook set!")

# --- Start Flask + Bot ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    print("🚀 Starting Flask server on port 8080...")
    app.run(host="0.0.0.0", port=8080)
