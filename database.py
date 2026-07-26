import aiosqlite
from datetime import datetime
from config import DB_NAME

ALLOWED_EDIT_FIELDS = {"title", "description", "genre", "year", "status", "poster"}


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                genre TEXT DEFAULT '',
                year INTEGER,
                status TEXT DEFAULT 'Davom etmoqda',
                poster TEXT,
                views INTEGER DEFAULT 0,
                created_at TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL,
                episode_number INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                added_at TEXT,
                FOREIGN KEY(anime_id) REFERENCES anime(id) ON DELETE CASCADE
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined_at TEXT,
                is_banned INTEGER DEFAULT 0
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                anime_id INTEGER,
                PRIMARY KEY (user_id, anime_id)
            )
            """
        )
        await db.commit()


# ---------------------------------------------------------------
# USERS
# ---------------------------------------------------------------
async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, joined_at) VALUES (?, ?, ?, ?)",
            (user_id, username or "", full_name or "", datetime.now().isoformat()),
        )
        await db.commit()


async def get_user_count() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE is_banned = 0")
        rows = await cur.fetchall()
        return [r[0] for r in rows]


# ---------------------------------------------------------------
# ANIME
# ---------------------------------------------------------------
async def add_anime(title, description, genre, year, status, poster) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            """INSERT INTO anime (title, description, genre, year, status, poster, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, genre, year, status, poster, datetime.now().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def get_anime_by_id(anime_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM anime WHERE id = ?", (anime_id,))
        return await cur.fetchone()


async def search_anime_by_name(query: str, limit: int = 20):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM anime WHERE title LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        return await cur.fetchall()


async def get_all_anime(page: int, per_page: int):
    offset = page * per_page
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM anime ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset)
        )
        return await cur.fetchall()


async def count_anime() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM anime")
        row = await cur.fetchone()
        return row[0] if row else 0


async def delete_anime(anime_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM anime WHERE id = ?", (anime_id,))
        await db.execute("DELETE FROM episodes WHERE anime_id = ?", (anime_id,))
        await db.execute("DELETE FROM favorites WHERE anime_id = ?", (anime_id,))
        await db.commit()


async def update_anime_field(anime_id: int, field: str, value):
    if field not in ALLOWED_EDIT_FIELDS:
        raise ValueError("Ruxsat etilmagan maydon")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE anime SET {field} = ? WHERE id = ?", (value, anime_id))
        await db.commit()


async def increment_views(anime_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE anime SET views = views + 1 WHERE id = ?", (anime_id,))
        await db.commit()


async def get_top_anime(limit: int = 5):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM anime ORDER BY views DESC LIMIT ?", (limit,))
        return await cur.fetchall()


# ---------------------------------------------------------------
# EPISODES
# ---------------------------------------------------------------
async def add_episode(anime_id: int, episode_number: int, file_id: str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            """INSERT INTO episodes (anime_id, episode_number, file_id, added_at)
               VALUES (?, ?, ?, ?)""",
            (anime_id, episode_number, file_id, datetime.now().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def get_episodes(anime_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM episodes WHERE anime_id = ? ORDER BY episode_number ASC",
            (anime_id,),
        )
        return await cur.fetchall()


async def get_episode(episode_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
        return await cur.fetchone()


async def count_episodes() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM episodes")
        row = await cur.fetchone()
        return row[0] if row else 0


async def delete_episode(episode_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
        await db.commit()


# ---------------------------------------------------------------
# FAVORITES
# ---------------------------------------------------------------
async def add_favorite(user_id: int, anime_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO favorites (user_id, anime_id) VALUES (?, ?)",
            (user_id, anime_id),
        )
        await db.commit()


async def remove_favorite(user_id: int, anime_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND anime_id = ?", (user_id, anime_id)
        )
        await db.commit()


async def is_favorite(user_id: int, anime_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND anime_id = ?", (user_id, anime_id)
        )
        return (await cur.fetchone()) is not None


async def get_favorites(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """SELECT anime.* FROM anime
               JOIN favorites ON anime.id = favorites.anime_id
               WHERE favorites.user_id = ? ORDER BY anime.id DESC""",
            (user_id,),
        )
        return await cur.fetchall()
