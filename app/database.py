import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "worldradio.db")


async def get_db() -> aiosqlite.Connection:
    """Return an open database connection. Caller is responsible for closing."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Create tables if they don't exist yet."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS play_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                country_code TEXT    NOT NULL,
                station_uuid TEXT    NOT NULL,
                station_name TEXT    NOT NULL,
                played_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Index makes the trending query fast even with millions of rows
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_play_events_station
            ON play_events (station_uuid)
        """)
        await db.commit()
