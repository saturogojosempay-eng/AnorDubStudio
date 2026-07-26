# ============================================================
#  UzumDub Studio Bot — Konfiguratsiya
# ============================================================
# LOKAL kompyuterda ishlatish uchun: pastdagi os.environ.get(...)
# ichidagi ikkinchi qiymatlarni o'zingizning haqiqiy
# ma'lumotlaringiz bilan almashtirishingiz mumkin.
#
# RENDER (yoki boshqa server) uchun: hech narsani bu faylda
# o'zgartirmang! Buning o'rniga Render dashboardida
# "Environment" bo'limiga quyidagi qiymatlarni environment
# variable sifatida qo'shing:
#   BOT_TOKEN, ADMIN_IDS, TURSO_DATABASE_URL, TURSO_AUTH_TOKEN
# Shunda kod ichida maxfiy ma'lumotlar saqlanmaydi va GitHub'ga
# xavfsiz push qilinadi.
# ============================================================

import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")

# ADMIN_IDS environment variable orqali keladi, masalan: "123456789,987654321"
_admin_ids_raw = os.environ.get("ADMIN_IDS", "123456789")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip()]

# ---------------------------------------------------------------
# Turso (libSQL) — bulutli, bepul va doimiy ma'lumotlar bazasi.
# Render qayta deploy qilinganda ham ma'lumotlar o'chib ketmaydi.
# turso.tech saytida bazangizni yaratganingizda beriladigan
# manzil va tokenni shu yerga (yoki Render Environment'ga) kiriting.
#
# Agar mahalliy kompyuterda, internet bazasisiz sinab ko'rmoqchi
# bo'lsangiz, TURSO_DATABASE_URL ni "file:uzumdub.db" qilib
# qoldiring — bu holda oddiy lokal fayl ishlatiladi (Render'da
# BUNI QILMANG, aks holda yana ma'lumot o'chib turadi).
# ---------------------------------------------------------------
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "file:uzumdub.db")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")

STUDIO_NAME = "UzumDub Studio"

# Bosh menyudagi banner matni (ixtiyoriy, /start da chiqadi)
WELCOME_TEXT = (
    "🍥 <b>{studio}</b> ga xush kelibsiz!\n\n"
    "Bu yerda siz sevimli animelaringizni o'zbek tilidagi dublyajda "
    "topishingiz mumkin.\n\n"
    "🔎 Anime nomi yoki <b>ID</b> raqami orqali qidiring\n"
    "📋 Barcha animelar ro'yxatini ko'ring\n"
    "⭐ Sevimlilarga qo'shib qo'ying\n\n"
    "Quyidagi tugmalardan birini tanlang 👇"
)

# Har bir sahifada nechta anime/qism ko'rsatilsin
ANIME_PER_PAGE = 6
EPISODES_PER_PAGE = 12