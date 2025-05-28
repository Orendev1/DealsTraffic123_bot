import os
import json
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import parse_affiliate_message

# Init logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials from environment
GOOGLE_CREDS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not GOOGLE_CREDS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON is missing in environment variables.")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in environment variables.")

SPREADSHEET_NAME = "Telegram Bot Deals"

# Setup Google Sheets
creds_dict = json.loads(GOOGLE_CREDS)
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    source = update.effective_chat.title or update.effective_user.username
    deals = parse_affiliate_message(text)

    for deal in deals:
        row = [
            datetime.utcnow().isoformat(),
            source,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("CPL", ""),
            deal.get("Deal Type", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            deal.get("CR", ""),
            text
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")

# Start bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
