
import os
import json
import logging
import telebot
import gspread
from google.oauth2 import service_account
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Load credentials from Railway ENV variable
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
creds_dict = json.loads(creds_json)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)

# Access spreadsheet
gc = gspread.authorize(credentials)
spreadsheet_name = os.getenv("SPREADSHEET_NAME")
worksheet = gc.open(spreadsheet_name).sheet1

# Set up Telegram bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = message.from_user.username or message.from_user.first_name or "Unknown"
        text = message.text.replace('\n', ' ').strip()
        row = [now, user, text]
        worksheet.append_row(row)
        bot.reply_to(message, "✅ Saved!")
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        bot.reply_to(message, "❌ Error saving your message.")

bot.polling()
