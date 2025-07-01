# -*- coding: utf-8 -*-
"""Utility class for broadcasting messages to users."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pathlib import Path
import logging

from telegram import Bot

from bot.subscriber_manager import subscriber_manager
from bot.config import BOT_TOKEN


logger = logging.getLogger(__name__)


class BroadcastManager:
    """Manage broadcasts with optional scheduling and segmentation."""

    def __init__(self, bot: Bot | None = None, *, storage: str = "broadcast_schedule.json", send_delay: float = 0.05):
        self.bot = bot or Bot(token=BOT_TOKEN)
        self.scheduled: List[tuple[datetime, asyncio.Task]] = []
        self.storage_path = Path(storage)
        self.lock = asyncio.Lock()
        self.send_delay = send_delay
        asyncio.get_event_loop().create_task(self._load_persisted())

    async def _load_persisted(self) -> None:
        try:
            if self.storage_path.exists():
                import json
                data = json.loads(self.storage_path.read_text())
                now = datetime.now(timezone.utc)
                for item in data:
                    when = datetime.fromisoformat(item["when"])
                    if when > now:
                        self.schedule(
                            when,
                            text=item.get("text"),
                            parse_mode=item.get("parse_mode"),
                            photo=item.get("photo"),
                            video=item.get("video"),
                            animation=item.get("animation"),
                            language=item.get("language"),
                            statuses=item.get("statuses"),
                            persist=False,
                        )
        except Exception as exc:
            logger.error("Failed to load scheduled broadcasts: %s", exc)

    async def _save_schedule(self) -> None:
        try:
            import json
            data = [
                {
                    "when": w.isoformat(),
                    "text": getattr(t, "_text", None),
                    "parse_mode": getattr(t, "_parse", None),
                    "photo": getattr(t, "_photo", None),
                    "video": getattr(t, "_video", None),
                    "animation": getattr(t, "_animation", None),
                    "language": getattr(t, "_language", None),
                    "statuses": getattr(t, "_statuses", None),
                }
                for w, t in self.scheduled
            ]
            self.storage_path.write_text(json.dumps(data))
        except Exception as exc:
            logger.error("Failed to save scheduled broadcasts: %s", exc)

    async def _remove_task(self, fut: asyncio.Task) -> None:
        async with self.lock:
            self.scheduled = [(w, t) for (w, t) in self.scheduled if t is not fut]
            await self._save_schedule()

    async def send(
        self,
        text: Optional[str] = None,
        parse_mode: Optional[str] = None,
        photo: Optional[str] = None,
        video: Optional[str] = None,
        animation: Optional[str] = None,
        language: Optional[str] = None,
        statuses: Optional[List[str]] = None,
    ) -> None:
        """Send a broadcast to users filtered by language and status."""
        users = await subscriber_manager.get_users(language=language, statuses=statuses)
        for user in users:
            try:
                if photo:
                    await self.bot.send_photo(
                        chat_id=user["user_id"],
                        photo=photo,
                        caption=text,
                        parse_mode=parse_mode,
                    )
                elif video:
                    await self.bot.send_video(
                        chat_id=user["user_id"],
                        video=video,
                        caption=text,
                        parse_mode=parse_mode,
                    )
                elif animation:
                    await self.bot.send_animation(
                        chat_id=user["user_id"],
                        animation=animation,
                        caption=text,
                        parse_mode=parse_mode,
                    )
                elif text:
                    await self.bot.send_message(
                        chat_id=user["user_id"],
                        text=text,
                        parse_mode=parse_mode,
                    )
            except Exception as exc:
                logger.error("Error broadcasting to %s: %s", user["user_id"], exc)
            await asyncio.sleep(self.send_delay)

    def schedule(
        self,
        when: datetime,
        *,
        text: Optional[str] = None,
        parse_mode: Optional[str] = None,
        photo: Optional[str] = None,
        video: Optional[str] = None,
        animation: Optional[str] = None,
        language: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        persist: bool = True,
    ) -> None:
        """Schedule a broadcast message."""
        now = datetime.now(timezone.utc)
        if when < now or when > now + timedelta(hours=72):
            raise ValueError("Broadcast time must be within 72 hours")
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(hours=24)
        count = sum(1 for t, _ in self.scheduled if day_start <= t < day_end)
        if count >= 12:
            raise ValueError("Maximum 12 scheduled messages per 24h")

        async def _task():
            delay = (when - datetime.now(timezone.utc)).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
            await self.send(
                text=text,
                parse_mode=parse_mode,
                photo=photo,
                video=video,
                animation=animation,
                language=language,
                statuses=statuses,
            )

        task = asyncio.create_task(_task())
        # store params on task for persistence
        task._text = text
        task._parse = parse_mode
        task._photo = photo
        task._video = video
        task._animation = animation
        task._language = language
        task._statuses = statuses

        async def _cleanup(fut: asyncio.Task) -> None:
            await self._remove_task(fut)

        async def _add_task():
            async with self.lock:
                self.scheduled.append((when, task))
                if persist:
                    await self._save_schedule()

        asyncio.get_event_loop().create_task(_add_task())
        task.add_done_callback(lambda fut: asyncio.get_event_loop().create_task(_cleanup(fut)))


broadcast_manager = BroadcastManager()
