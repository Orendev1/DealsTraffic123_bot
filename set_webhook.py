import asyncio
from telegram import Bot

BOT_TOKEN = "7443002644:AAG6-qjA1nYIiipMDf6e8KO1Dkw18jyQatQ"
WEBHOOK_URL = "https://dealstraffic123bot-production.up.railway.app/webhook"

async def set_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook()
    await bot.set_webhook(url=WEBHOOK_URL)

asyncio.run(set_webhook())
