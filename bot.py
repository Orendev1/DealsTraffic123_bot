
import os
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import parse_deals

# Load keywords from JSON
def load_keywords(file_path='keywords.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Determine if a message qualifies as a deal based on keyword categories
def is_deal_message(text, keywords):
    text_lower = text.lower()
    matched_categories = set()
    for category, terms in keywords.items():
        for term in terms:
            if term.lower() in text_lower:
                matched_categories.add(category)
                break
    return len(matched_categories) >= 2

# Google Sheets setup
def setup_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('google-credentials.json', scope)
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
            context.application.sheet.append_row(row)
