from zipfile import ZipFile

# Corrected version without lookbehind regex
corrected_bot_py = '''
import os
import re
import json
import telebot
import gspread
from datetime import datetime
from google.oauth2 import service_account

# === ENV VARIABLES ===
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === GOOGLE SHEETS AUTH ===
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
creds_dict = json.loads(creds_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
gc = gspread.authorize(credentials)
worksheet = gc.open(SPREADSHEET_NAME).sheet1

# === TELEGRAM BOT ===
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# === REGEX PATTERNS ===
DOLLAR_PATTERN = re.compile(r'(\\$?\\d{2,5})')
PERCENT_PATTERN = re.compile(r'(\\d{1,2})\\s*%')
CPA_CRG_PATTERN = re.compile(r'(\\$?\\d{2,5})\\s*\\+\\s*(\\d{1,2})%')

# === HELPERS ===
def parse_message_block(block, sender, raw_message):
    geo_match = re.match(r'^([A-Z]{2}|GCC|LATAM|ASIA|NORDICS)', block.strip(), re.IGNORECASE)
    geo = geo_match.group(1).upper() if geo_match else None

    cpa = None
    crg = None

    if match := CPA_CRG_PATTERN.search(block):
        cpa = int(re.sub(r'\\D', '', match.group(1)))
        crg = int(match.group(2))
    elif match := DOLLAR_PATTERN.search(block):
        cpa = int(re.sub(r'\\D', '', match.group(1)))

    if not crg and (match := PERCENT_PATTERN.search(block)):
        crg = int(match.group(1))

    funnels = ', '.join(re.findall(r'(Immediate\\w+|Bitcoin\\w+|Trader\\w+|GPT\\w+|Btc\\w+|https?://\\S+|\\b[A-Z][a-zA-Z]+AI\\b)', block)) or ''

    source_match = re.search(r'(SEO|PPC|YouTube|Facebook|Google|Native|Search|Taboola|Unity Ads)', block, re.IGNORECASE)
    source = source_match.group(0).title() if source_match else ''

    cap_match = re.search(r'(\\d{1,4})\\s*(caps|leads|cap)', block, re.IGNORECASE)
    cap = int(cap_match.group(1)) if cap_match else None

    return {
        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Affiliate Name': sender,
        'Geo': geo,
        'CPA': cpa,
        'CG%': crg,
        'Funnels': funnels,
        'Source Type': source,
        'Quantity': cap,
        'Comments': '',
        'Raw Message': raw_message.strip()
    }

def extract_deals_from_text(text, sender):
    deals = []
    lines = text.splitlines()
    current_block = ""
    for line in lines:
        if re.match(r'^([A-Z]{2}|GCC|LATAM|ASIA|NORDICS)\\b', line.strip(), re.IGNORECASE):
            if current_block:
                deal = parse_message_block(current_block, sender, text)
                if deal['Geo']:
                    deals.append(deal)
            current_block = line
        else:
            current_block += "\\n" + line
    if current_block:
        deal = parse_message_block(current_block, sender, text)
        if deal['Geo']:
            deals.append(deal)
    return deals

# === HANDLE MESSAGES ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    sender = message.chat.title or message.chat.username or 'Unknown'
    print(f"📩 Message from {sender}: {message.text[:60]}...")

    deals = extract_deals_from_text(message.text, sender)
    print(f"🔍 Parsed {len(deals)} deals")

    for deal in deals:
        row = [deal[h] for h in ['Date', 'Affiliate Name', 'Geo', 'CPA', 'CG%', 'Funnels', 'Source Type', 'Quantity', 'Comments', 'Raw Message']]
        worksheet.append_row(row)
        print(f"✅ Row written: {deal['Geo']}")

print("🤖 Bot is running... waiting for messages.")
bot.polling()
'''

# Create the updated ZIP
zip_path = "/mnt/data/bot-parser-fixed.zip"
with ZipFile(zip_path, "w") as zipf:
    zipf.writestr("bot.py", corrected_bot_py)

zip_path
