import logging
import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Google Sheets setup
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(open(CREDENTIALS_PATH, "r").read())
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    user = update.effective_user.username or update.effective_chat.title or "Unknown"

    try:
        deals = parse_affiliate_message(message)
        for deal in deals:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user,
                deal.get("GEO", ""),
                deal.get("CPA", ""),
                deal.get("CRG", ""),
                deal.get("Funnels", ""),
                deal.get("Source", ""),
                deal.get("Cap", ""),
                message,
            ]
            sheet.append_row(row, value_input_option="USER_ENTERED")
    except Exception as e:
        logger.error(f"Failed to process message: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
