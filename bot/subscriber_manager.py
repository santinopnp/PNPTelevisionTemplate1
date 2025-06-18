# bot/subscriber_manager.py
"""Manage subscriber data using a PostgreSQL database."""

import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List

from bot.config import CHANNELS, PLANS, BOT_TOKEN, DATABASE_URL
from telegram import Bot


class SubscriberManager:
    def __init__(self, db_url: str = DATABASE_URL):
        if not db_url:
            raise ValueError("DATABASE_URL must be provided")
        self.conn = psycopg2.connect(db_url)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
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
        self.conn.commit()

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

            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO subscribers (user_id, plan, start_date, expires_at, transaction_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        plan=EXCLUDED.plan,
                        start_date=EXCLUDED.start_date,
                        expires_at=EXCLUDED.expires_at,
                        transaction_id=EXCLUDED.transaction_id
                    """,
                    (user_id, plan_name, start_date, expiry_date, transaction_id),
                )
            self.conn.commit()

            bot = Bot(token=BOT_TOKEN)
            for channel in CHANNELS.values():
                try:
                    await bot.add_chat_members(chat_id=channel, user_ids=[user_id])
                except Exception as e:
                    print(f"Error adding user {user_id} to {channel}: {e}")
            return True
        except Exception as e:
            print(f"Error adding subscriber: {e}")
            return False

    def get_all(self) -> List[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id, expires_at FROM subscribers")
            rows = cur.fetchall()
        return [
            {"user_id": row[0], "expires_at": row[1]} for row in rows
        ]

    def get_stats(self) -> Dict[str, int]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM subscribers")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM subscribers WHERE expires_at > NOW()")
            active = cur.fetchone()[0]
        return {"total": total, "active": active}


subscriber_manager = SubscriberManager()
