import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from config import BOT_TOKEN
import database as db
from handlers import user, admin


# ---------------------------------------------------------------
# Render (yoki boshqa hosting) botni "uxlab qolishdan" saqlash uchun
# juda kichik veb-server. UptimeRobot shu manzilga muntazam so'rov
# yuborib turadi, Render esa "trafik bor" deb hisoblab, xizmatni
# uyg'oq ushlab turadi. Bot funksionalligiga bu hech qanday
# ta'sir qilmaydi — Telegram bilan aloqa alohida ishlaydi.
#
# MUHIM: bu server Telegram bilan bog'lanishdan OLDIN ishga
# tushirilishi kerak — aks holda Render portni vaqtida topa
# olmay, deploy'ni "Timed Out" deb bekor qiladi.
# ---------------------------------------------------------------
async def handle_ping(request):
    return web.Response(text="🍥 UzumDub Studio bot ishlayapti!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Ping-server {port}-portda ishga tushdi")


async def main():
    logging.basicConfig(level=logging.INFO)

    # 1) Avval veb-serverni ishga tushiramiz — Render portni darhol
    #    ko'rishi va deploy'ni muvaffaqiyatli deb belgilashi uchun.
    await start_web_server()

    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("❗️ BOT_TOKEN topilmadi! config.py yoki environment variable orqali kiriting.")
        # Port ochiq qolishi uchun dastur shu yerda to'xtamaydi,
        # lekin Telegram bilan ishlamaydi.
        await asyncio.Event().wait()
        return

    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Admin router birinchi ulanadi (admin tugmalari user routerdagi
    # umumiy matn handlerlaridan oldin ushlanishi uchun)
    dp.include_router(admin.router)
    dp.include_router(user.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"⚠️ delete_webhook xatosi (davom etamiz): {e}")

    print("🍥 UzumDub Studio bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")