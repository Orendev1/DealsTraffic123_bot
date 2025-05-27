import os
import json
import re
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.request import HTTPXRequest
from parser import parse_deals

# Load keywords from JSON
def load_keywords(file_path='keywords.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Determine if a message qualifies as a deal
def is_deal_message(text, keywords):
    text_lower = text.lower()
    matched_categories = set()
    for category, terms in keywords.items():
        for term in terms:
            if term.lower() in text_lower:
                matched_categories.add(category)
                break
    return len(matched_categories) >= 2

# Setup Google Sheets
def setup_google_sheets():
    json_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not json_creds:
        raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable")

    service_account_info = json.loads(json_creds)
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open("Telegram Bot Deals").sheet1
    return sheet

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    if not hasattr(context.application, "keywords"):
        context.application.keywords = load_keywords()

    if not hasattr(context.application, "sheet"):
        context.application.sheet = setup_google_sheets()

    if is_deal_message(text, context.application.keywords):
        deals = parse_deals(text)
        for deal in deals:
            row = [
                update.message.date.isoformat(),
                update.effective_chat.title or update.effective_user.username,
                deal.get("GEO"),
                deal.get("CPA"),
                deal.get("CRG"),
                deal.get("CPL"),
                deal.get("Deal Type"),
                deal.get("Funnel"),
                deal.get("Source"),
                deal.get("Cap"),
                deal.get("CR"),
                text  # raw message
            ]
            context.application.sheet.append_row(row, value_input_option="USER_ENTERED")

# Start the bot
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable")

    # Add timeout handling for stability
    request = HTTPXRequest(read_timeout=10, write_timeout=10, connect_timeout=5)

    app = ApplicationBuilder().token(token).request(request).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
