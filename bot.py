import os
import re
import datetime
import telebot
import gspread
from google.oauth2 import service_account

# Load environment variables
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    "credentials/google-credentials.json", scopes=scope
)
gc = gspread.authorize(credentials)
worksheet = gc.open(SPREADSHEET_NAME).sheet1

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Pattern definitions
GEO_PATTERN = re.compile(r"(?<=\n|\s|^)([A-Z]{2}|GCC|LATAM|ASIA|NORDICS)(?=\s|:|$)", re.IGNORECASE)
CPA_PATTERN = re.compile(r"\b(?:CPA|CPL|FLAT)?\s*[:=]?\s*\$?(\d{2,5})(?:\s*\+\s*(\d{1,2})%?)?", re.IGNORECASE)
CRG_PATTERN = re.compile(r"CR(?:G)?[:=]?\s*(\d{1,2})%", re.IGNORECASE)
FUNNEL_PATTERN = re.compile(r"Funnels?:?\s*(.*?)(?:\n|$)", re.IGNORECASE)
SOURCE_PATTERN = re.compile(r"Source:?\s*(SEO|PPC|YouTube|Facebook|Google|Native|Taboola|Search)", re.IGNORECASE)
CAP_PATTERN = re.compile(r"Cap:?\s*(\d{1,4})", re.IGNORECASE)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    sender = message.from_user.username or message.from_user.first_name or "Unknown"
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    geo_blocks = re.split(r"(?=\b[A-Z]{2}\b|\bGCC\b|\bLATAM\b|\bASIA\b|\bNORDICS\b)", text)
    for block in geo_blocks:
        geo_match = GEO_PATTERN.search(block)
        if not geo_match:
            continue

        geo = geo_match.group(1).upper()
        cpa = ""
        crg = ""
        funnels = ""
        source = ""
        cap = ""
        raw = block.strip()

        cpa_match = CPA_PATTERN.search(block)
        if cpa_match:
            amount = cpa_match.group(1)
            crg_bonus = cpa_match.group(2)
            cpa = f"${amount}"
            if crg_bonus:
                crg = f"{crg_bonus}%"

        crg_match = CRG_PATTERN.search(block)
        if crg_match:
            crg = f"{crg_match.group(1)}%"

        funnel_match = FUNNEL_PATTERN.search(block)
        if funnel_match:
            funnels = funnel_match.group(1).strip()

        source_match = SOURCE_PATTERN.search(block)
        if source_match:
            source = source_match.group(1)

        cap_match = CAP_PATTERN.search(block)
        if cap_match:
            cap = cap_match.group(1)

        row = [date, sender, geo, cpa, crg, funnels, source, cap, raw]
        worksheet.append_row(row)

        bot.reply_to(message, "✅ Saved!")

# Start polling
bot.polling(non_stop=True)
