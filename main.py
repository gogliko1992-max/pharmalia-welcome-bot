import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pharmalia-webhook")

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")  # e.g. https://pharmalia-welcome-bot-abcde-uc.a.run.app
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}" if WEBHOOK_BASE else None

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_BASE is not set")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# === handlers ===
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Привет 👋 Бот на связи! Пиши что-нибудь.")

@dp.message_handler()
async def echo_handler(message: types.Message):
    text = message.text or "медиа ✅"
    await message.answer(f"Получил: {text}")

# === aiohttp routes ===
async def handle_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        data = {}
    update = types.Update(**data)
    await dp.process_update(update)
    return web.Response(text="ok")

async def health(request: web.Request) -> web.Response:
    return web.Response(text="ok")

async def on_startup(app: web.Application):
    from aiogram.utils import exceptions
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await bot.set_webhook(WEBHOOK_URL, max_connections=40, allowed_updates=["message", "chat_member"])
        logger.info(f"Webhook set to: {WEBHOOK_URL}")
    except exceptions.TelegramAPIError as e:
        logger.exception(f"Failed to set webhook: {e}")

async def on_cleanup(app: web.Application):
    await bot.session.close()

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
