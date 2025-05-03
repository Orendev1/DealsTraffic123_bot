import telebot
import requests
import datetime
import os
from flask import Flask, request

# טוקן של הבוט
BOT_TOKEN = "7652567138:AAFwyX0Cc7cgwzQhz37LnvnSoweyC778YbE"

# כתובת API של Sheet.best
SHEETBEST_API_URL = "https://api.sheetbest.com/sheets/5a048120-f758-4f56-9e45-d059bac1f2bf"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# פונקציה ששולחת טקסט לטבלת גוגל שיטס
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

# מטפל בהודעות נכנסות
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    parse_and_send_to_sheet(message.text)

# הגדרת ה־Webhook
@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200

if __name__ == "__main__":
    WEBHOOK_URL = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'your-subdomain.railway.app')}"
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
