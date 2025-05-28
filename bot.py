# bot.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from parser import parse_affiliate_message
import os
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    sender = update.message.chat.title or update.message.chat.username or "Unknown"

    deals = parse_affiliate_message(message_text)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for deal in deals:
        row = [
            timestamp,
            sender,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message_text  # Raw message
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")

# Main app
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
