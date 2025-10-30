import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions

# === Настройки логов ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pharmalia-webhook")

# === Переменные окружения ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")  # например: https://pharmalia-welcome-bot-xxx.a.run.app
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}" if WEBHOOK_BASE else None

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is not set")
if not WEBHOOK_URL:
    raise RuntimeError("❌ WEBHOOK_BASE is not set")

# === Инициализация бота ===
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

# === Хендлер приветствия ===
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def greet_new_member(message: types.Message):
    for member in message.new_chat_members:
        await message.reply(f"👋 Добро пожаловать, {member.first_name}! Вы в *Pharmalia*.")

# === Команда /start ===
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Привет 👋 Бот на связи! Пиши что-нибудь или добавь меня в группу.")

# === Echo (для теста) ===
@dp.message_handler()
async def echo_handler(message: types.Message):
    text = message.text or "медиа ✅"
    await message.answer(f"Получил: {text}")

# === Webhook обработчик ===
async def handle_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.process_update(update)
    except Exception as e:
        logger.exception(f"Ошибка обработки webhook: {e}")
        return web.Response(status=500, text="error")
    return web.Response(text="ok")

# === Health-check (для Cloud Run) ===
async def health(request: web.Request) -> web.Response:
    return web.Response(text="ok")

# === Запуск / остановка ===
async def on_startup(app: web.Application):
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            WEBHOOK_URL,
            max_connections=40,
            allowed_updates=["message", "chat_member"]
        )
        logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
    except exceptions.TelegramAPIError as e:
        logger.exception(f"Ошибка установки webhook: {e}")

async def on_cleanup(app: web.Application):
    await bot.session.close()
    logger.info("🧹 Сессия бота закрыта.")

# === Создание aiohttp приложения ===
def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    web.run_app(app, host="0.0.0.0", port=port)
