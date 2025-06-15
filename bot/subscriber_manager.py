# bot/subscriber_manager.py
import json
import os
from datetime import datetime, timedelta
from typing import Dict
from bot.config import CHANNELS, PLANS
from telegram import Bot
from bot.config import BOT_TOKEN

class SubscriberManager:
    """Manage subscriber access to channels"""

    def __init__(self, db_file: str = "subscribers.json"):
        self.db_file = db_file
        self.subscribers = self._load_subscribers()

    def _load_subscribers(self) -> Dict:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"users": {}, "stats": {"total": 0, "active": 0}}

    def _save_subscribers(self):
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscribers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving subscribers: {e}")

    async def add_subscriber(self, user_id: int, plan_name: str, transaction_id: str = None) -> bool:
        try:
            user_id_str = str(user_id)

            plan_info = None
            for key, info in PLANS.items():
                if info["name"] == plan_name:
                    plan_info = info
                    break

            if not plan_info:
                return False

            duration_days = plan_info["duration_days"]
            start_date = datetime.now()
            expiry_date = start_date + timedelta(days=duration_days)

            self.subscribers["users"][user_id_str] = {
                "plan": plan_name,
                "start_date": start_date.isoformat(),
                "expires_at": expiry_date.isoformat(),
                "transaction_id": transaction_id
            }
            self._save_subscribers()

            bot = Bot(token=BOT_TOKEN)
            for channel in CHANNELS.values():
                try:
                    invite_link = await bot.export_chat_invite_link(chat_id=channel)
                    await bot.send_message(chat_id=user_id, text=f"Join channel: {invite_link}")
                except Exception as e:
                    print(f"Error inviting user {user_id} to {channel}: {e}")

            return True

        except Exception as e:
            print(f"Error adding subscriber: {e}")
            return False

    def get_stats(self):
        active = 0
        now = datetime.now()
        for data in self.subscribers["users"].values():
            try:
                if datetime.fromisoformat(data["expires_at"]) > now:
                    active += 1
            except:
                continue

        return {
            "total": len(self.subscribers["users"]),
            "active": active
        }

subscriber_manager = SubscriberManager()
