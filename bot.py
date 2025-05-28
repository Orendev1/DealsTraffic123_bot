# bot.py
import os
import json
import logging
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google.oauth2.service_account import Credentials
from parser import parse_affiliate_message
from datetime import datetime
from flask import Flask, request
import asyncio
import traceback
import threading

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = "Telegram Bot Deals"
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN or not CREDENTIALS_JSON:
    raise ValueError("Missing environment variables.")

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON), scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

application = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = update.effective_user.username or update.effective_user.first_name or "Unknown"
    deals = parse_affiliate_message(message)

    print("🔍 Parsed deals:")
    print(json.dumps(deals, indent=2))

    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("CPL", ""),
            "CPA" if "CPA" in deal else "CPL" if "CPL" in deal else "",
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message[:300] + "..." if len(message) > 300 else message
        ]
        sheet.append_row(row)

application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "Bot is running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
        loop.close()
        return "ok", 200
    except Exception:
        logging.error("Webhook error:\n" + traceback.format_exc())
        return "error", 500

async def setup_bot():
    await application.initialize()
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    print("✅ Bot initialized and webhook set!")

if __name__ == "__main__":
    def run_flask():
        print(f"🚀 Starting Flask server on port {PORT}...")
        app.run(host="0.0.0.0", port=PORT)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(setup_bot())
