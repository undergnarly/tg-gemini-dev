import logging
import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api_gateway:8000")

# --- Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Welcome! I am your autonomous development assistant. Send me a task.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages and forward them to the API gateway."""
    user_id = update.message.from_user.id
    text = update.message.text
    logger.info(f"Received message from user {user_id}: '{text}'")

    task_payload = {
        "user_id": user_id,
        "text": text,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_GATEWAY_URL}/tasks/", json=task_payload, timeout=30.0)
            response.raise_for_status() # Will raise an exception for 4xx/5xx responses
        
        await update.message.reply_text("✅ Task received! The AI crew is on it. I'll get back to you with the result.")

    except httpx.ConnectError:
        logger.error("Connection to API gateway failed.")
        await update.message.reply_text("❌ An error occurred: Could not connect to the API gateway. Please try again later.")
    except httpx.HTTPStatusError as e:
        logger.error(f"API gateway returned an error: {e.response.status_code} - {e.response.text}")
        await update.message.reply_text(f"❌ An error occurred: The API gateway is not responding correctly. (Code: {e.response.status_code})")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text("❌ An unexpected error occurred. Please check the logs.")


def main() -> None:
    """Starts the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN is not set. The bot cannot start.")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment or .env file")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main() 