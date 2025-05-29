# bot.py
import os
import json
import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    MessageHandler, 
    filters
)

from parser import parse_affiliate_message

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- ENV ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Telegram Bot Deals")
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # without /webhook, e.g., https://your-app.up.railway.app

if not BOT_TOKEN or not CREDENTIALS_JSON or not WEBHOOK_URL:
    raise ValueError("Missing required environment variables.")

# --- Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON), scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# --- Telegram App ---
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

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL + "/webhook",
    )
    print("✅ Bot is ready and webhook is running.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
