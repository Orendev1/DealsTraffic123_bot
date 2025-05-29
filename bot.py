import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from parser import parse_deal_message
from sheets import update_sheet

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
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

# Initialize bot
application = Application.builder().token(TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and parse deals"""
    try:
        message = update.message
        if not message or not message.text:
            return

        # Log the incoming message
        logger.info(f"Received message: {message.text}")

        # Parse the deal message
        deals = parse_deal_message(message.text)
        
        if deals:
            # Update Google Sheets with the parsed deals
            for deal in deals:
                update_sheet(deal)
            logger.info(f"Successfully parsed and updated {len(deals)} deals")
        else:
            logger.info("No deals found in message")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

# Add handlers
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook requests from Telegram"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return jsonify({"status": "ok"})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Set webhook URL (you'll need to set this up with Telegram)
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        application.bot.set_webhook(url=webhook_url)
    
    # Run Flask app
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000))) 