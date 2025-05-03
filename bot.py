import telebot
import requests
import datetime

# טוקן הבוט
BOT_TOKEN = "7652567138:AAFwyX0Cc7cgwzQhz37LnvnSoweyC778YbE"

# כתובת API של Sheet.best
SHEETBEST_API_URL = "https://api.sheetbest.com/sheets/5a048120-f758-4f56-9e45-d059bac1f2bf"

bot = telebot.TeleBot(BOT_TOKEN)

# פונקציית עיבוד ושליחה לגוגל שיט
def parse_and_send_to_sheet(text):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    data = {
        "Date": now,
        "AFF NAME": "",
        "GEO": "",
        "CPA": "",
        "CG%": "",
        "Funnels": "",
        "Source Type": "",
        "Cap": "",
        "Raw Message": text
    }

    try:
        response = requests.post(SHEETBEST_API_URL, json=data)
        print("Data sent:", response.status_code)
    except Exception as e:
        print("Error sending to sheet:", e)

# קבלת הודעות מהמשתמש
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    parse_and_send_to_sheet(message.text)

# הפעלת הבוט
bot.infinity_polling()
