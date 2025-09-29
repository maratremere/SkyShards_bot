import psycopg2
import asyncio
from datetime import datetime
from typing import List
import pytz
from config import LOCAL_TIMEZONE

# ----------------- PostgreSQL -----------------

def get_connection(db_url: str):
    return psycopg2.connect(db_url)

def init_db_sync(db_url: str) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            user_id BIGINT PRIMARY KEY,
            chat_id BIGINT NOT NULL,
            last_seen TEXT,
            language TEXT,
            timezone TEXT,
            notify BOOLEAN DEFAULT TRUE,
            notify_mute BOOLEAN DEFAULT FALSE
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()

def upsert_chat_sync(db_url: str, user_id: int, chat_id: int,
                     language: str | None = None,
                     timezone: str | None = None,
                     notify: bool | None = None,
                     notify_mute: bool | None = None) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    now = datetime.now(pytz.timezone(LOCAL_TIMEZONE)).isoformat()
    cur.execute(
        """
        INSERT INTO chats(user_id, chat_id, last_seen, language, timezone, notify, notify_mute)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            chat_id = EXCLUDED.chat_id,
            last_seen = EXCLUDED.last_seen,
            language = COALESCE(EXCLUDED.language, chats.language),
            timezone = COALESCE(EXCLUDED.timezone, chats.timezone),
            notify = COALESCE(EXCLUDED.notify, chats.notify),
            notify_mute = COALESCE(EXCLUDED.notify_mute, chats.notify_mute)
        """,
        (
            user_id, chat_id, now, language, timezone,
            notify if notify is not None else None,
            notify_mute if notify_mute is not None else None
        ),
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_chat_ids_sync(db_url: str) -> List[int]:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chats")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]

# ------- language -------
def get_user_language_sync(db_url: str, user_id: int) -> str | None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT language FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row and row[0] is not None else None

def set_user_language_sync(db_url: str, user_id: int, language: str) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_url, user_id, chat_id, language)
    cur.close()
    conn.close()

# ------- timezone -------
def get_user_timezone_sync(db_url: str, user_id: int) -> str | None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT timezone FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row and row[0] is not None else None

def set_user_timezone_sync(db_url: str, user_id: int, timezone: str) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_url, user_id, chat_id, timezone=timezone)
    cur.close()
    conn.close()

# ------- notify -------
def get_user_notify_sync(db_url: str, user_id: int) -> bool:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT notify FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row[0]) if row and row[0] is not None else True  #по умолчанию True

def set_user_notify_sync(db_url: str, user_id: int, notify: bool) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_url, user_id, chat_id, notify=notify)
    cur.close()
    conn.close()

# ------- notify_mute -------
def get_user_notify_mute_sync(db_url: str, user_id: int) -> bool:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT notify_mute FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row[0]) if row and row[0] is not None else False  #по умолчанию False

def set_user_notify_mute_sync(db_url: str, user_id: int, notify_mute: bool) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    chat_id = row[0] if row else user_id
    upsert_chat_sync(db_url, user_id, chat_id, notify_mute=notify_mute)
    cur.close()
    conn.close()

# ----------------- Async wrappers -----------------
async def upsert_chat(
            db_url: str, 
            user_id: int, 
            chat_id: int,
            language: str | None = None, 
            timezone: str | None = None, 
            notify: bool | None = None, 
            notify_mute: bool | None = None
    ) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, upsert_chat_sync, db_url, 
        user_id, chat_id, language, 
        timezone, notify, notify_mute
    )

async def get_all_chat_ids(db_url: str) -> List[int]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_all_chat_ids_sync, db_url)

async def get_user_language(db_url: str, user_id: int) -> str | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_language_sync, db_url, user_id)

async def set_user_language(db_url: str, user_id: int, language: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_language_sync, db_url, user_id, language)

async def get_user_timezone(db_url: str, user_id: int) -> str | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_timezone_sync, db_url, user_id)

async def set_user_timezone(db_url: str, user_id: int, timezone: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_timezone_sync, db_url, user_id, timezone)

async def get_user_notify(db_url: str, user_id: int) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_notify_sync, db_url, user_id)

async def set_user_notify(db_url: str, user_id: int, notify: bool) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_notify_sync, db_url, user_id, notify)

async def get_user_notify_mute(db_url: str, user_id: int) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_notify_mute_sync, db_url, user_id)

async def set_user_notify_mute(db_url: str, user_id: int, notify_mute: bool) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_user_notify_mute_sync, db_url, user_id, notify_mute)

# ------- delete user -------
def delete_user_sync(db_url: str, user_id: int) -> None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("DELETE FROM chats WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

async def delete_user(db_url: str, user_id: int) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, delete_user_sync, db_url, user_id)

# ------- cleanup inactive users -------
def cleanup_inactive_users_sync(db_url: str, days: int = 90) -> int:
    """
    Удаляет пользователей, которые не появлялись в боте указанное количество дней
    Возвращает количество удалённых строк
    """
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM chats
        WHERE last_seen IS NOT NULL
        AND last_seen::timestamptz < (NOW() - INTERVAL '%s days')
        """,
        (days,)
    )
    deleted_count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return deleted_count

async def cleanup_inactive_users(db_url: str, days: int = 90) -> int:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, cleanup_inactive_users_sync, db_url, days)

# ----------------- last_seen -----------------
def get_user_last_seen_sync(db_url: str, user_id: int) -> datetime | None:
    conn = get_connection(db_url)
    cur = conn.cursor()
    cur.execute("SELECT last_seen FROM chats WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row[0]:
        return datetime.fromisoformat(row[0])
    return None

async def get_user_last_seen(db_url: str, user_id: int) -> datetime | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_user_last_seen_sync, db_url, user_id)
