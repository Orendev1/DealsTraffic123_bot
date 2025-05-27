import telebot
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import re
import json
from google.oauth2 import service_account
import gspread

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
creds_dict = json.loads(creds_json)

bot = telebot.TeleBot(BOT_TOKEN)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1

HEADERS = [
    "Affiliate Name (telegram group name)",
    "Geo",
    "CPA",
    "CG%",
    "Funnels",
    "source type",
    "quantity of leads aff can send",
    "comments",
    "last update date"
]
if sheet.row_count == 0 or sheet.row_values(1) != HEADERS:
    sheet.resize(1)
    sheet.append_row(HEADERS)

def extract_deals_from_text(text, group_name):
    deals = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(r"\b[A-Z]{2}\b", line) or re.search(r"\ud83c", line):
            country_codes = re.findall(r"\b[A-Z]{2}\b", line)
            country_codes = [c for c in country_codes if c.upper() != "CR"]
            if not country_codes:
                continue
            funnel = line.split("—")[-1].strip() if "—" in line else line.strip()
            price_line = next((l for l in lines[i:i+4] if "price" in l.lower()), "")
            cpa = extract_price(price_line)
            cg = extract_percent(price_line)
            comment = "GEOs: " + ", ".join(country_codes) if len(country_codes) > 1 else ""
            for code in country_codes:
                deals.append([
                    group_name,
                    code,
                    cpa,
                    cg,
                    funnel,
                    "",
                    extract_cap(text),
                    comment,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
    return deals

def extract_price(line):
    match = re.search(r"PRICE[:\s]+(\d{2,5})\$", line)
    return int(match.group(1)) if match else ""

def extract_percent(line):
    match = re.search(r"\+(\d{1,2})%", line)
    return int(match.group(1)) / 100 if match else ""

def extract_cap(text):
    cap_match = re.search(r"cap(?:acity)?[\s:]*([\d]{1,5})", text, re.IGNORECASE)
    return cap_match.group(1) if cap_match else ""

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text
    group_name = message.chat.title or message.chat.username or message.chat.first_name or "unknown"
    deals = extract_deals_from_text(text, group_name)
    for deal in deals:
        sheet.append_row(deal)
    print(f"✅ Saved {len(deals)} deal(s)")

print("🤖 Bot is running... waiting for messages.")
bot.infinity_polling()
