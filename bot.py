# bot.py
import logging
import os
import json
import telegram
from telegram.ext import ApplicationBuilder, MessageHandler, filters
import gspread
from google.oauth2 import service_account
from parser import parse_affiliate_message

# קונפיגורציית לוגים
logging.basicConfig(level=logging.INFO)

# משתנים מהסביבה
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = os.getenv("SHEET_NAME", "Telegram Bot Deals")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# אימות עם Google Sheets
creds_dict = json.loads(GOOGLE_CREDENTIALS)
credentials = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
gc = gspread.authorize(credentials)
sheet = gc.open(GOOGLE_SHEET_NAME).sheet1

# פונקציה לכתיבה לגוגל שיטס
def write_to_sheet(parsed_deals, message, username):
    for deal in parsed_deals:
        row = {
            "Date": message.date.strftime("%Y-%m-%d %H:%M"),
            "From": username,
            "GEO": deal.get("GEO", ""),
            "CPA": deal.get("CPA", ""),
            "CRG": deal.get("CRG", ""),
            "Funnels": deal.get("Funnels", ""),
            "Source": deal.get("Source", ""),
            "Cap": deal.get("Cap", ""),
            "Raw Message": message.text.strip()
        }
        sheet.append_row(list(row.values()))

# פונקציית הטיפול בהודעות
async def handle_message(update, context):
    message = update.message
    if not message or not message.text:
        return

    parsed_deals = parse_affiliate_message(message.text)
    if parsed_deals:
        username = message.from_user.username or message.from_user.full_name
        write_to_sheet(parsed_deals, message, username)

# הרצת הבוט
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
