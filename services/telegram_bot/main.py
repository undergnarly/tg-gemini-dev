import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment or .env file")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я готов к работе. Отправь мне задачу.",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /help is issued."""
    await update.message.reply_text("Просто отправь мне текстовое сообщение с описанием задачи, и я передам ее команде разработчиков.")

async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the user's task to the API Gateway."""
    user_id = update.effective_user.id
    task_text = update.message.text
    logger.info(f"Received task from user {user_id}: {task_text}")
    
    await update.message.reply_text(f"Получил твою задачу: \"{task_text}\". Отправляю ее команде...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_GATEWAY_URL}/tasks/",
                json={"user_id": user_id, "text": task_text},
                timeout=30.0
            )
            response.raise_for_status() # Вызовет исключение для кодов 4xx/5xx
            
            receipt = response.json()
            logger.info(f"Task sent successfully. Receipt: {receipt}")
            await update.message.reply_text(f"Задача принята в работу! ID твоей задачи: `{receipt.get('task_id')}`")

    except httpx.RequestError as exc:
        logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        await update.message.reply_text("Не удалось связаться с командой разработчиков. Попробуй позже.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text("Произошла непредвиденная ошибка. Мы уже разбираемся.")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - handle the task
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_task))

    logger.info("Telegram Bot is starting...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Telegram Bot has stopped.")

if __name__ == "__main__":
    main() 