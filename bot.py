import telebot
from flask import Flask, request
import requests
import datetime
import os

BOT_TOKEN = "7652567138:AAFwyX0Cc7cgwzQhz37LnvnSoweyC778YbE"
bot = telebot.TeleBot(BOT_TOKEN)

SHEETBEST_API_URL = "https://api.sheetbest.com/sheets/5a048120-f758-4f56-9e45-d059bac1f2bf"

app = Flask(__name__)

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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    parse_and_send_to_sheet(message.text)

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/', methods=['GET'])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://dealstraffic123bot-production.up.railway.app/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=port)
