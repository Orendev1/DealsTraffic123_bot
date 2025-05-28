import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from parser import parse_affiliate_message
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in environment variables.")

if not GOOGLE_CREDENTIALS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON is missing in environment variables.")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Google Sheets
creds_dict = json.loads(GOOGLE_CREDENTIALS)
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
gc = gspread.authorize(credentials)

# Open the spreadsheet (change to your sheet name if needed)
SPREADSHEET_NAME = "Telegram Bot Deals"
sheet = gc.open(SPREADSHEET_NAME).sheet1

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if not message:
        return

    deals = parse_affiliate_message(message)
    if not deals:
        return

    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update.effective_chat.title or update.effective_user.username,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message  # raw message
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
