# bot/subscriber_manager.py
"""Manage subscriber data using a PostgreSQL database asynchronously."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import logging

try:
    import asyncpg
except ImportError as exc:
    raise ImportError(
        "asyncpg is required. Install dependencies using 'pip install -r requirements.txt'"
    ) from exc
from bot.config import CHANNELS, PLANS, BOT_TOKEN, DATABASE_URL
from bot.db_migrations import apply_migrations
import sys

logger = logging.getLogger(__name__)
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

        # Apply database migrations to keep schema up to date
        loop.run_until_complete(apply_migrations(self.pool))


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
            # Use timezone-aware UTC datetime to avoid deprecation warning
            start_date = datetime.now(timezone.utc)
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
                    logger.error("Error inviting user %s to %s: %s", user_id, channel, e)
            await self.record_user(user_id)
            return True
        except Exception as e:
            logger.error("Error adding subscriber: %s", e)
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

    async def record_user(self, user_id: int, language: str | None = None) -> None:
        """Insert or update a user in the tracking table."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO users (user_id, language, last_seen)
                    VALUES ($1, $2, NOW())
                    ON CONFLICT (user_id) DO UPDATE SET
                        language=COALESCE($2, users.language),
                        last_seen=NOW()
                    """,
                    user_id,
                    language,
                )
        except Exception as e:
            logger.error("Error recording user %s: %s", user_id, e)
            raise

    async def get_users(
        self,
        *,
        language: str | None = None,
        statuses: List[str] | None = None,
    ) -> List[Dict]:
        """Return users optionally filtered by language and subscription status."""
        try:
            async with self.pool.acquire() as conn:
                now = datetime.now(timezone.utc)
                base = """
                    WITH data AS (
                        SELECT u.user_id, u.language,
                               CASE
                                   WHEN s.expires_at IS NULL THEN 'never'
                                   WHEN s.expires_at > $1 THEN 'active'
                                   ELSE 'churned'
                               END AS status
                        FROM users u
                        LEFT JOIN subscribers s ON u.user_id = s.user_id
                    )
                    SELECT user_id, language, status FROM data
                """
                args = [now, language, statuses]
                query = base + " WHERE ($2::text IS NULL OR language = $2)"
                query += " AND ($3::text[] IS NULL OR status = ANY($3))"
                rows = await conn.fetch(query, *args)
        except Exception as e:
            logger.error("Error getting users: %s", e)
            raise

        return [
            {"user_id": r["user_id"], "language": r["language"], "status": r["status"]}
            for r in rows
        ]


if "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv):
    subscriber_manager = None
else:
    subscriber_manager = SubscriberManager()
