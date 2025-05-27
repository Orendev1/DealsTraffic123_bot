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
CPA_PATTERN = re.compile(r"CPA[:\s\-]*\$?(\d{2,5})", re.IGNORECASE)
CRG_PATTERN = re.compile(r"\+?\s*(\d{1,2})%\s*(?:CR|CRG|Conv|Conversion Guarantee)?", re.IGNORECASE)
FUNNEL_PATTERN = re.compile(r"Funnels?:\s*(.+?)(?=\n|Source|Traffic|Cap|\Z)", re.IGNORECASE | re.DOTALL)
SOURCE_PATTERN = re.compile(r"(?:Source|Traffic):\s*([\w/\-+ ]+)", re.IGNORECASE)
CAP_PATTERN = re.compile(r"Cap[:\s]+(\d{1,4})", re.IGNORECASE)
NEGOTIATION_PATTERN = re.compile(r"\b(?:can we do|negotiate|instead|work on|maybe|can you reduce|let's make it)\b", re.IGNORECASE)

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
    matches = list(GEO_PATTERN.finditer(text))
    if not matches:
        return [{"geo": "", "raw_message": text}]

    deals = []
    for i, match in enumerate(matches):
        geo = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        deal = {
            "geo": geo,
            "raw_message": block,
            "tag": "Negotiation" if NEGOTIATION_PATTERN.search(block) else ""
        }

        if (m := CPA_PATTERN.search(block)):
            deal["cpa"] = int(m.group(1))
        if (m := CRG_PATTERN.search(block)):
            deal["crg"] = int(m.group(1))
        if (m := FUNNEL_PATTERN.search(block)):
            cleaned = m.group(1).replace("\n", ", ")
            deal["funnels"] = ", ".join([f.strip() for f in cleaned.split(",") if f.strip()])
        if (m := SOURCE_PATTERN.search(block)):
            deal["source"] = m.group(1).strip()
        if (m := CAP_PATTERN.search(block)):
            deal["cap"] = int(m.group(1))

        deals.append(deal)

    return deals

# === Start Bot ===
bot.polling()
