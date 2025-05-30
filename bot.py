import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from parser import parse_deal_message
from sheets import update_sheet
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get bot token from environment
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

# Initialize bot
application = Application.builder().token(TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        if not message or not message.text:
            logger.info("No message or text found in update.")
            return

        logger.info(f"Received message: {message.text}")

        deals = parse_deal_message(message.text)
        if deals:
            for deal in deals:
                update_sheet(deal)
            logger.info(f"Successfully parsed and updated {len(deals)} deals")
        else:
            logger.info("No deals found in message")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)

# Add handlers
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Webhook data: {data}")
        update = Update.de_json(data, application.bot)
        logger.info("Processing update with telegram bot...")
        asyncio.run(application.process_update(update))
        logger.info("Update processed successfully.")
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Exception in /webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Set webhook URL (רצוי להגדיר ידנית מחוץ לקוד, או עם סקריפט נפרד)
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        try:
            logger.info(f"Setting webhook to: {webhook_url}")
            asyncio.run(application.bot.set_webhook(url=webhook_url))
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}", exc_info=True)

    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)))
