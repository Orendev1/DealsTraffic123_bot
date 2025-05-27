import os
import telebot
import gspread
from datetime import datetime
from google.oauth2 import service_account

# --- Load ENV variables ---
spreadsheet_name = os.getenv("SPREADSHEET_NAME")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Authenticate with Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_file(
    "credentials/google-credentials.json", scopes=scope
)
gc = gspread.authorize(credentials)
worksheet = gc.open(spreadsheet_name).sheet1

# --- Telegram Bot ---
bot = telebot.TeleBot(telegram_token)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print("📩 Message received from:", message.from_user.username)
    print("🔹 Content:", message.text)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Simple raw insert: [Date, AFF NAME, GEO, CPA, CG%, Funnels, Source Type, Cap, Raw Message]
    row = [
        now,
        message.from_user.username,
        "", "", "", "", "", "",  # Placeholder fields to be parsed later
        message.text
    ]

    worksheet.append_row(row)
    print("✅ Row written to Google Sheet")

bot.polling()
