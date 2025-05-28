import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from parser import parse_affiliate_message
from sheets import append_to_sheet

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    message_text = update.message.text or ""
    username = update.effective_user.username or "Unknown"
    chat_title = update.effective_chat.title or username or "Private Chat"

    logger.info(f"Received message from {chat_title}: {message_text[:50]}...")

    try:
        parsed_rows = parse_affiliate_message(message_text, chat_title)
        if parsed_rows:
            append_to_sheet(parsed_rows)
        else:
            logger.info("No relevant data extracted from message.")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

# Main entry
if __name__ == '__main__':
    logger.info("Starting Telegram bot...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
