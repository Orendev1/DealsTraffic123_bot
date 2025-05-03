import os
import telebot
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user.username or message.from_user.first_name
    text = message.text
    time = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    print(f"[{time}] {user}: {text}")
    # כאן בהמשך נוסיף את הקוד שממפה את המידע ומעדכן את האקסל

bot.polling()
