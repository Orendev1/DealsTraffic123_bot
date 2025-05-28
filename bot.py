# bot.py
import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from parser import parse_affiliate_message
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env vars
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
SPREADSHEET_NAME = "Telegram Bot Deals"

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing")
if not GOOGLE_CREDENTIALS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON is missing")

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDENTIALS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    raw_text = update.message.text
    if not raw_text:
        return

    sender = update.effective_chat.title or update.effective_user.username or "Unknown"
    deals = parse_affiliate_message(raw_text)

    for deal in deals:
        row = [
            datetime.utcnow().isoformat(),
            sender,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("CPL", ""),
            deal.get("Deal Type", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            "",  # CR – can be added later
            raw_text
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")

# Start app
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook setup
async def main():
    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    logger.info("Webhook set to %s", WEBHOOK_URL)
    await app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
