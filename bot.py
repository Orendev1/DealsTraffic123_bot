import os
import telebot
import gspread
import pandas as pd
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
bot = telebot.TeleBot(TOKEN)

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_file("credentials/google-credentials.json", scopes=scope)
gc = gspread.authorize(credentials)
sh = gc.open(SPREADSHEET_NAME)
worksheet = sh.sheet1

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    worksheet.append_row([message.text])
    bot.reply_to(message, "✅ Message logged!")

bot.infinity_polling()
