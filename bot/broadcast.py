# -*- coding: utf-8 -*-
"""Utilities for sending broadcast messages to user groups."""
import json
import os
from datetime import datetime
from typing import List, Dict

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.subscriber_manager import subscriber_manager


class BroadcastManager:
    """Store broadcast subscription preferences."""

    def __init__(self, file: str = "data/broadcast_prefs.json") -> None:
        self.file = file
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.file):
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"unsubscribed": []}
        else:
            self.data = {"unsubscribed": []}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.file), exist_ok=True)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def is_unsubscribed(self, user_id: int) -> bool:
        return user_id in self.data.get("unsubscribed", [])

    def unsubscribe(self, user_id: int) -> None:
        if user_id not in self.data.get("unsubscribed", []):
            self.data.setdefault("unsubscribed", []).append(user_id)
            self._save()

    def subscribe(self, user_id: int) -> None:
        if user_id in self.data.get("unsubscribed", []):
            self.data["unsubscribed"].remove(user_id)
            self._save()


broadcast_manager = BroadcastManager()


def _load_interactions() -> List[int]:
    users: List[int] = []
    path = os.path.join("data", "interactions.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                logs = json.load(f)
            users = [int(entry.get("user_id")) for entry in logs]
        except Exception:
            pass
    return list(set(users))


def get_user_groups() -> Dict[str, List[int]]:
    """Return user IDs grouped by purchase status."""
    now = datetime.now()
    subs = subscriber_manager.subscribers.get("users", {})

    active: List[int] = []
    churned: List[int] = []
    for uid, data in subs.items():
        try:
            exp = datetime.fromisoformat(data.get("expires_at"))
            if exp > now:
                active.append(int(uid))
            else:
                churned.append(int(uid))
        except Exception:
            churned.append(int(uid))

    all_users = set(_load_interactions()) | {int(u) for u in subs.keys()}
    never_purchased = [uid for uid in all_users if str(uid) not in subs]

    return {
        "ALL": list(all_users),
        "NEVER_PURCHASED": never_purchased,
        "ACTIVE_MEMBER": active,
        "CHURNED": churned,
    }


async def send_broadcast(
    bot: Bot,
    group: str,
    message: str,
    photo: str | None = None,
    video: str | None = None,
) -> int:
    """Send a broadcast message to a user group."""
    groups = get_user_groups()
    targets = groups.get(group.upper())
    if targets is None:
        raise ValueError("Invalid group")

    targets = [uid for uid in targets if not broadcast_manager.is_unsubscribed(uid)]
    if not targets:
        return 0

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Unsubscribe ❌", callback_data="broadcast_unsub")]]
    )

    sent = 0
    for uid in targets:
        try:
            if video:
                await bot.send_video(chat_id=uid, video=video, caption=message, parse_mode="Markdown", reply_markup=keyboard)
            elif photo:
                await bot.send_photo(chat_id=uid, photo=photo, caption=message, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await bot.send_message(chat_id=uid, text=message, parse_mode="Markdown", reply_markup=keyboard)
            sent += 1
        except Exception as e:
            print(f"Error sending to {uid}: {e}")
    return sent


async def handle_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback to unsubscribe from broadcasts."""
    query = update.callback_query
    await query.answer("Unsubscribed")
    broadcast_manager.unsubscribe(query.from_user.id)
    await query.edit_message_reply_markup(None)
