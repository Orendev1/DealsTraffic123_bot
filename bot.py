
import telebot
import os
import pandas as pd
import gspread
from datetime import datetime
from google.oauth2 import service_account

# Load credentials from file
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_file("google-credentials.json", scopes=scope)

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")

# Connect to Google Sheets
gc = gspread.authorize(credentials)
sh = gc.open(SPREADSHEET_NAME)
worksheet = sh.sheet1

# Start the Telegram bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

headers = ['Affiliate Name', 'Geo', 'CPA', 'CG%', 'Funnels', 'Source Type', 'Quantity', 'Comments', 'Last Update']
if worksheet.row_values(1) != headers:
    worksheet.insert_row(headers, index=1)

def extract_price(text):
    import re
    match = re.search(r'\$?(\d+(?:\.\d{1,2})?)', text)
    return float(match.group(1)) if match else None

def extract_percent(text):
    import re
    match = re.search(r'(\d{1,2}(?:\.\d{1,2})?)\s*%', text)
    return float(match.group(1)) if match else None

def extract_cap(text):
    import re
    match = re.search(r'Cap\s*:?\s*(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else None

def extract_deals_from_text(text, group_name):
    geo = None
    cpa = None
    cg_percent = None
    funnel = None
    cap = None

    lines = text.split('\n')
    for line in lines:
        if not geo and len(line.strip()) in [2, 3]:
            geo = line.strip().upper()
        if 'CPA' in line.upper() or '$' in line:
            cpa = extract_price(line)
        if '%' in line:
            cg_percent = extract_percent(line)
        if 'funnel' in line.lower() or 'traffic' in line.lower():
            funnel = line.strip()
        if 'cap' in line.lower():
            cap = extract_cap(line)

    return {
        'Affiliate Name': group_name,
        'Geo': geo,
        'CPA': cpa,
        'CG%': cg_percent,
        'Funnels': funnel,
        'Source Type': '',
        'Quantity': cap,
        'Comments': '',
        'Last Update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    group_name = message.chat.title or message.chat.username or "Unknown"
    deal_data = extract_deals_from_text(message.text, group_name)
    row = [deal_data[h] for h in headers]
    worksheet.append_row(row)
    print(f"✅ New deal added from {group_name}")

print("🤖 Bot is running... waiting for messages.")
bot.polling()
