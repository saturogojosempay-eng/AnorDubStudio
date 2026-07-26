# ============================================================
#  UzumDub Studio Bot — Konfiguratsiya
# ============================================================
# 1) @BotFather dan olingan tokenni pastga qo'ying
# 2) O'zingizning Telegram ID raqamingizni ADMIN_IDS ro'yxatiga qo'shing
#    (ID ni bilmasangiz @userinfobot ga /start yozing)
# ============================================================

BOT_TOKEN = "8005337101:AAErrzx_y3SaBJB9lGquGXHCvjRsBN9yfN0"

ADMIN_IDS = [
    8888728779
]

DB_NAME = "uzumdub.db"

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
