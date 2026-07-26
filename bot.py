import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database as db
from handlers import user, admin


async def main():
    logging.basicConfig(level=logging.INFO)

    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("❗️ config.py faylida BOT_TOKEN ni to'g'ri kiriting!")
        return

    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Admin router birinchi ulanadi (admin tugmalari user routerdagi
    # umumiy matn handlerlaridan oldin ushlanishi uchun)
    dp.include_router(admin.router)
    dp.include_router(user.router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("🍥 UzumDub Studio bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
