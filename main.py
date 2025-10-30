import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")  # https://...run.app
PORT = int(os.getenv("PORT", "8080"))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBHOOK_BASE:
    logger.warning("WEBHOOK_BASE is not set. Webhook will fail to register until set correctly.")

# ВАЖНО: путь совпадает с тем, что уже стоит в getWebhookInfo
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}" if WEBHOOK_BASE else None

bot = Bot(token=TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def on_start_cmd(message: types.Message):
    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("📅 Записаться", url="https://t.me/Pharmalia")
    )
    await message.answer("👋 Добро пожаловать в PHARMALIA!\nНажмите кнопку ниже, чтобы записаться.", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def greet_new_member(message: types.Message):
    for member in message.new_chat_members:
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📅 Записаться", url="https://t.me/Pharmalia")
        )
        text = (
            f"👋 Добро пожаловать, {member.first_name}!\n\n"
            "🌿 *Pharmalia Clinic Batumi* — забота о вашем здоровье.\n"
            "💉 **УЗИ**, **Анализы**, **Гинекология**, **Вакцинация**\n"
            "🧒 **Педиатрия**, **Эндокринология**, **Гастроэнтерология**\n"
            "♿ **Реабилитация**, **Форма 100**, **Капельницы**, **Урология**\n\n"
            "📍 Батум, Вахтанг Горгасали 4\n"
            "📞 +995 593 50 93 57\n\n"
            "📅 Нажмите «Записаться» и отправьте номер администратору 👇"
        )
        await message.reply(text, reply_markup=kb)

async def on_startup(dp):
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    else:
        logger.error("WEBHOOK_BASE is empty; cannot set webhook.")

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=PORT,
    )
