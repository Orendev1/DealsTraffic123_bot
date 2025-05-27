import telebot
import os
import re
import json
from datetime import datetime
import gspread
from google.oauth2 import service_account

# === Load ENV ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")

# === Load Google Credentials from env var ===
service_account_info = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# === Init Bot ===
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# === Patterns ===
GEO_PATTERN = re.compile(r"(?<!\w)([A-Z]{2}|GCC|LATAM|ASIA|NORDICS)(?=\s|:|\n)")
CPA_PATTERN = re.compile(r"\$?(\d{2,5})\s*(?:\+\s*\d{1,2}%\s*CRG)?")
CRG_PATTERN = re.compile(r"(\d{1,2})%\s*(?:CR|CRG)", re.IGNORECASE)
FUNNEL_PATTERN = re.compile(r"Funnels?:\s*(.+?)(?=\n|Source|\Z)", re.IGNORECASE | re.DOTALL)
SOURCE_PATTERN = re.compile(r"(?:Source|Traffic):\s*(SEO|PPC|YouTube|Facebook|Google|Native|Search|Taboola|.*?)\s*(?=\n|Cap|\Z)", re.IGNORECASE)
CAP_PATTERN = re.compile(r"Cap[:\s]+(\d{1,4})", re.IGNORECASE)

# === Message Handling ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    username = message.from_user.username or message.from_user.first_name
    deals = extract_deals(text)
    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            deal.get("geo", ""),
            deal.get("raw_geo_block", ""),
            deal.get("cpa", ""),
            deal.get("crg", ""),
            deal.get("funnels", ""),
            deal.get("source", ""),
            deal.get("cap", ""),
            text,
            deal.get("tag", "")
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        bot.reply_to(message, "✅ Saved!")

def extract_deals(text):
    geos = GEO_PATTERN.findall(text)
    deals = []

    for geo in geos:
        deal = {"geo": geo, "raw_geo_block": "", "tag": ""}
        block_pattern = re.compile(rf"{geo}[^\n]*((?:\n.*?)*?)(?=\n[A-Z]{{2}}|\Z)", re.IGNORECASE)
        block_match = block_pattern.search(text)
        if block_match:
            block = f"{geo}{block_match.group(1)}".strip()
            deal["raw_geo_block"] = block
            if any(phrase in block.lower() for phrase in ["negotiate", "instead", "can we do", "could we", "work on"]):
                deal["tag"] = "Negotiation"

            if match := CPA_PATTERN.search(block):
                deal["cpa"] = int(match.group(1))
            if match := CRG_PATTERN.search(block):
                deal["crg"] = int(match.group(1))
            if match := FUNNEL_PATTERN.search(block):
                deal["funnels"] = match.group(1).strip()
            if match := SOURCE_PATTERN.search(block):
                deal["source"] = match.group(1).strip()
            if match := CAP_PATTERN.search(block):
                deal["cap"] = int(match.group(1))

            deals.append(deal)

    return deals

# === Start Bot ===
bot.polling()
