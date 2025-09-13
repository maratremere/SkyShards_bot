import logging
import psycopg2
from datetime import datetime
from config import DATABASE_URL

class PostgresLogHandler(logging.Handler):
    def __init__(self, db_url: str):
        super().__init__()
        self.db_url = db_url

        # создаём таблицу, если её ещё нет
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT NOW(),
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
                """)
                conn.commit()

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO logs (created_at, level, message) VALUES (%s, %s, %s)",
                        (datetime.now(), record.levelname, log_entry)
                    )
                    conn.commit()
        except Exception as e:
            # чтобы при падении базы логгер не сломал бота
            print("Failed to write log to DB:", e)

# ---------------- Использование ----------------
logger = logging.getLogger("tg_bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#пишем в базу
pg_handler = PostgresLogHandler(DATABASE_URL)
pg_handler.setFormatter(formatter)
logger.addHandler(pg_handler)
