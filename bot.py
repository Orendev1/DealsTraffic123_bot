# bot.py
import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Telegram Bot Deals")

# Fail early if credentials are missing
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in environment variables.")
if not GOOGLE_CREDENTIALS_JSON:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON is missing in environment variables.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Google Sheets credentials from JSON string
creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
credentials = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    parsed_deals = parse_affiliate_message(message_text)

    if not parsed_deals:
        return  # Do not respond or write anything if it's not a deal

    for deal in parsed_deals:
        row = [
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            update.message.chat.title or update.message.chat.username or "Private",
            message_text
        ]
        sheet.append_row(row)

# Set up bot app
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

if __name__ == "__main__":
    logger.info("Starting bot...")
    app.run_polling()
