import sqlite3
import asyncio
from datetime import datetime
from typing import List
import pytz
from config import LOCAL_TIMEZONE

# ----------------- SQLite -----------------

def init_db_sync(db_file: str) -> None:
    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            user_id INTEGER PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            last_seen TEXT,
            language TEXT,
            timezone TEXT,
            notify INTEGER DEFAULT 1,
            notify_mute INTEGER DEFAULT 1
        )
        """
    )
    conn.commit()
    conn.close()

def upsert_chat_sync(db_file: str, user_id: int, chat_id: int,
                     language: str | None = None,
                     timezone: str | None = None,
                     notify: bool | None = None,
                     notify_mute: bool | None = None) -> None:
    conn = sqlite3.connect(db_file)
    now = datetime.now(pytz.timezone(LOCAL_TIMEZONE)).isoformat()
    conn.execute(
        """
        INSERT INTO chats(user_id, chat_id, last_seen, language, timezone, notify, notify_mute)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            chat_id=excluded.chat_id,
            last_seen=excluded.last_seen,
            language=COALESCE(excluded.language, language),
            timezone=COALESCE(excluded.timezone, timezone),
            notify=COALESCE(excluded.notify, notify),
            notify_mute=COALESCE(excluded.notify_mute, notify_mute)
        """,
        (
            user_id, chat_id, now, language, timezone, 
            int(notify) if notify is not None else None, 
            int(notify_mute) if notify_mute is not None else None
        ),
    )
    conn.commit()
    conn.close()

def get_all_chat_ids_sync(db_file: str) -> List[int]:
    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT chat_id FROM chats").fetchall()
    conn.close()
    return [r[0] for r in rows]
# ------- language -------
def get_user_language_sync(db_file: str, user_id: int) -> str | None:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT language FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else None

def set_user_language_sync(db_file: str, user_id: int, language: str) -> None:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT chat_id FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_file, user_id, chat_id, language)
    conn.close()
# ------- timezone -------
def get_user_timezone_sync(db_file: str, user_id: int) -> str | None:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT timezone FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else None

def set_user_timezone_sync(db_file: str, user_id: int, timezone: str) -> None:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT chat_id FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_file, user_id, chat_id, timezone=timezone)
    conn.close()
# ------- notify -------
def get_user_notify_sync(db_file: str, user_id: int) -> bool:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT notify FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return bool(row[0]) if row and row[0] is not None else True  #по умолчанию True

def set_user_notify_sync(db_file: str, user_id: int, notify: bool) -> None:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT chat_id FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_file, user_id, chat_id, notify=notify)
    conn.close()
# ------- notify_mute -------
def get_user_notify_mute_sync(db_file: str, user_id: int) -> bool:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT notify_mute FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return bool(row[0]) if row and row[0] is not None else False  #по умолчанию False

def set_user_notify_mute_sync(db_file: str, user_id: int, notify_mute: bool) -> None:
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT chat_id FROM chats WHERE user_id = ?", (user_id,)).fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_file, user_id, chat_id, notify_mute=notify_mute)
    conn.close()

# ----------------- Async wrappers -----------------
async def upsert_chat(
            db_file: str, 
            user_id: int, 
            chat_id: int,
            language: str | None = None, 
            timezone: str | None = None, 
            notify: bool | None = None, 
            notify_mute: bool | None = None
    ) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, upsert_chat_sync, db_file, 
        user_id, chat_id, language, 
        timezone, notify, notify_mute
    )

async def get_all_chat_ids(db_file: str) -> List[int]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_all_chat_ids_sync, db_file)

async def get_user_language(db_file: str, user_id: int) -> str | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_language_sync, db_file, user_id)

async def set_user_language(db_file: str, user_id: int, language: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_language_sync, db_file, user_id, language)

async def get_user_timezone(db_file: str, user_id: int) -> str | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_timezone_sync, db_file, user_id)

async def set_user_timezone(db_file: str, user_id: int, timezone: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_timezone_sync, db_file, user_id, timezone)

async def get_user_notify(db_file: str, user_id: int) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_notify_sync, db_file, user_id)

async def set_user_notify(db_file: str, user_id: int, notify: bool) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_notify_sync, db_file, user_id, notify)

async def get_user_notify_mute(db_file: str, user_id: int) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_notify_mute_sync, db_file, user_id)

async def set_user_notify_mute(db_file: str, user_id: int, notify_mute: bool) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_notify_mute_sync, db_file, user_id, notify_mute)
