# bot/subscriber_manager.py
"""Manage subscriber data using a PostgreSQL database asynchronously."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

try:
    import asyncpg
except ImportError as exc:
    raise ImportError(
        "asyncpg is required. Install dependencies using 'pip install -r requirements.txt'"
    ) from exc
from bot.config import CHANNELS, PLANS, BOT_TOKEN, DATABASE_URL
from telegram import Bot


class SubscriberManager:
    def __init__(self, db_url: str = DATABASE_URL):
        if not db_url:
            raise ValueError("DATABASE_URL must be provided")
        self.db_url = db_url
        loop = asyncio.get_event_loop()
        try:
            self.pool = loop.run_until_complete(asyncpg.create_pool(dsn=db_url))
        except Exception as exc:
            raise ConnectionError(
                "Could not connect to the database. Check DATABASE_URL and that the server is running."
            ) from exc
        loop.run_until_complete(self._ensure_table())

    async def _ensure_table(self) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id BIGINT PRIMARY KEY,
                    plan TEXT NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    transaction_id TEXT
                )
                """
            )

    async def add_subscriber(self, user_id: int, plan_name: str, transaction_id: str = None) -> bool:
        try:
            plan_info = None
            for key, info in PLANS.items():
                if info["name"] == plan_name:
                    plan_info = info
                    break
            if not plan_info:
                return False

            duration_days = plan_info["duration_days"]
            start_date = datetime.utcnow()
            expiry_date = start_date + timedelta(days=duration_days)

            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO subscribers (user_id, plan, start_date, expires_at, transaction_id)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id) DO UPDATE SET
                        plan=EXCLUDED.plan,
                        start_date=EXCLUDED.start_date,
                        expires_at=EXCLUDED.expires_at,
                        transaction_id=EXCLUDED.transaction_id
                    """,
                    user_id,
                    plan_name,
                    start_date,
                    expiry_date,
                    transaction_id,
                )

            bot = Bot(token=BOT_TOKEN)
            for channel in CHANNELS.values():
                try:
                    invite_link = await bot.export_chat_invite_link(chat_id=channel)
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"Join {channel}: {invite_link}",
                    )
                except Exception as e:
                    print(f"Error inviting user {user_id} to {channel}: {e}")
            return True
        except Exception as e:
            print(f"Error adding subscriber: {e}")
            return False

    async def get_all(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id, expires_at FROM subscribers")
        return [
            {"user_id": row[0], "expires_at": row[1]} for row in rows
        ]

    async def get_stats(self) -> Dict[str, int]:
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM subscribers")
            active = await conn.fetchval(
                "SELECT COUNT(*) FROM subscribers WHERE expires_at > NOW()"
            )
        return {"total": total, "active": active}


subscriber_manager = SubscriberManager()
