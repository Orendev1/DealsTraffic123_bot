import os
import json
import gspread
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message
from flask import Flask, request

# קריאה למשתני סביבה
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = "Telegram Bot Deals"
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # הגדר את זה בריילווי

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in environment variables.")
if not GOOGLE_CREDENTIALS:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON is missing in environment variables.")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing in environment variables.")

# התחברות ל-Google Sheets
creds_dict = json.loads(GOOGLE_CREDENTIALS)
creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# הגדרת Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running with webhook!'

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot.application.bot)
    bot.application.update_queue.put(update)
    return 'ok'

# הגדרת בוט
bot = Application.builder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or ""
    if not message_text.strip():
        return

    rows = parse_affiliate_message(message_text)
    for row in rows:
        values = [
            update.effective_chat.title or update.effective_chat.username or "Private",
            update.effective_user.full_name,
            row.get('GEO', ''),
            row.get('CPA', ''),
            row.get('CRG', ''),
            row.get('Funnels', ''),
            row.get('Source', ''),
            row.get('Cap', ''),
            message_text
        ]
        sheet.append_row(values)

bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    import threading
    import telegram

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    threading.Thread(target=run_flask).start()

    telegram_bot = bot.bot
    telegram_bot.delete_webhook()
    telegram_bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}")
    bot.run_polling()  # נדרש כדי שה-queue תעבוד, אבל לא ישתמש ב־getUpdates
