# bot.py
import os
import json
import logging
from datetime import datetime

import gspread
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
from google.oauth2.service_account import Credentials

from parser import parse_affiliate_message

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- ENV ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Telegram Bot Deals")
CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not CREDENTIALS_JSON or not WEBHOOK_URL:
    raise ValueError("Missing environment variables")

# --- Google Auth ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON), scopes=scopes)
gc = gspread.authorize(creds)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# --- Flask App & Telegram Application ---
app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = update.effective_user.username or update.effective_user.first_name or "Unknown"
    deals = parse_affiliate_message(message)

    for deal in deals:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            deal.get("GEO", ""),
            deal.get("CPA", ""),
            deal.get("CRG", ""),
            deal.get("Funnels", ""),
            deal.get("Source", ""),
            deal.get("Cap", ""),
            message[:500],
        ]
        sheet.append_row(row)

telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.route("/")
def index():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put(update)
        return "ok"
    return "invalid", 400

# --- Run webhook setup on launch ---
import asyncio
async def setup():
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

asyncio.run(setup())
