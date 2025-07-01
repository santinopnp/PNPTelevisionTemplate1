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
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_subscribers_expires_at ON subscribers (expires_at)"
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY
                )
                """
            )
            await conn.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT"
            )
            await conn.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP NOT NULL DEFAULT NOW()"
            )
            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_language ON users (language)"
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

    async def get_users(
        self,
        *,
        language: str | None = None,
        statuses: List[str] | None = None,
    ) -> List[Dict]:
        """Return users optionally filtered by language and subscription status."""
        async with self.pool.acquire() as conn:
            now = datetime.now(timezone.utc)
            query = """
                SELECT u.user_id, u.language,
                       CASE
                           WHEN s.expires_at IS NULL THEN 'never'
                           WHEN s.expires_at > $1 THEN 'active'
                           ELSE 'churned'
                       END AS status
                FROM users u
                LEFT JOIN subscribers s ON u.user_id = s.user_id
            """
            args = [now]
            conditions = []
            if language:
                args.append(language)
                conditions.append(f"u.language = ${len(args)}")
            if statuses:
                placeholders = ", ".join(f"${len(args) + i + 1}" for i in range(len(statuses)))
                conditions.append(
                    f"(CASE WHEN s.expires_at IS NULL THEN 'never' WHEN s.expires_at > $1 THEN 'active' ELSE 'churned' END) IN ({placeholders})"
                )
                args.extend(statuses)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            rows = await conn.fetch(query, *args)

        return [
            {"user_id": r["user_id"], "language": r["language"], "status": r["status"]}
            for r in rows
        ]


if "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv):
    subscriber_manager = None
else:
    subscriber_manager = SubscriberManager()
