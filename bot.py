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

# === Setup Google Sheets ===
json_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not json_creds:
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable")

service_account_info = json.loads(json_creds)
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# === Init Bot ===
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# === Patterns ===
GEO_PATTERN = re.compile(r"(?<!\w)([A-Z]{2}|GCC|LATAM|ASIA|NORDICS)(?=\s|:|\n)")
CPA_PATTERN = re.compile(r"\bCPA[:\s\-]*\$?(\d{2,5})\b", re.IGNORECASE)
CRG_PATTERN = re.compile(r"(\d{1,2})%\s*(?:CR|CRG|Conv|Conversion Guarantee)?", re.IGNORECASE)
FUNNEL_PATTERN = re.compile(r"Funnels?:\s*(.+?)(?=\n|Source|Traffic|Cap|\Z)", re.IGNORECASE | re.DOTALL)
SOURCE_PATTERN = re.compile(r"(?:Source|Traffic):\s*([\w/\-+ ]+)", re.IGNORECASE)
CAP_PATTERN = re.compile(r"Cap[:\s]+(\d{1,4})", re.IGNORECASE)
NEGOTIATION_PATTERN = re.compile(r"\b(?:can we do|negotiate|instead|work on|maybe)\b", re.IGNORECASE)

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
            deal.get("cpa", ""),
            deal.get("crg", ""),
            deal.get("funnels", ""),
            deal.get("source", ""),
            deal.get("cap", ""),
            deal.get("tag", ""),
            deal.get("raw_message", text)
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        bot.reply_to(message, "✅ Saved!")

def extract_deals(text):
    geos = GEO_PATTERN.findall(text)
    deals = []
    for geo in geos:
        deal = {"geo": geo, "tag": ""}
        block_pattern = re.compile(rf"{geo}[^\n]*((?:\n.*?)*?)(?=\n[A-Z]{{2}}|\nGCC|\nLATAM|\nASIA|\nNORDICS|\Z)", re.IGNORECASE)
        block_match = block_pattern.search(text)
        if block_match:
            block = f"{geo}{block_match.group(1)}".strip()
            deal["raw_message"] = block

            if NEGOTIATION_PATTERN.search(block):
                deal["tag"] = "Negotiation"

            cpa_match = CPA_PATTERN.search(block)
            crg_match = CRG_PATTERN.search(block)
            funnel_match = FUNNEL_PATTERN.search(block)
            source_match = SOURCE_PATTERN.search(block)
            cap_match = CAP_PATTERN.search(block)

            if cpa_match:
                deal["cpa"] = int(cpa_match.group(1))
            if crg_match:
                deal["crg"] = int(crg_match.group(1))
            if funnel_match:
                cleaned = funnel_match.group(1).replace("\n", ", ")
                deal["funnels"] = ", ".join([f.strip() for f in cleaned.split(",") if f.strip()])
            if source_match:
                deal["source"] = source_match.group(1).strip()
            if cap_match:
                deal["cap"] = int(cap_match.group(1))

            deals.append(deal)
    return deals

# === Start Bot ===
bot.polling()
