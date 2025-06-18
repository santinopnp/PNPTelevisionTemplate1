from datetime import datetime
from telegram import Bot
from bot.config import BOT_TOKEN, CHANNELS
from bot.subscriber_manager import subscriber_manager

bot = Bot(token=BOT_TOKEN)


async def check_expired_users():
    expired_users = []
    now = datetime.now()

    for uid, data in subscriber_manager.subscribers.get("users", {}).items():
        if "expires_at" in data:
            try:
                exp_date = datetime.fromisoformat(data["expires_at"])
                if exp_date < now:
                    expired_users.append(int(uid))
            except Exception:
                continue

    for user_id in expired_users:
        for channel in CHANNELS.values():
            try:
                await bot.ban_chat_member(chat_id=channel, user_id=user_id)
                await bot.unban_chat_member(chat_id=channel, user_id=user_id)
                print(f"Removed expired user: {user_id}")
            except Exception as e:
                print(f"Error removing {user_id}: {e}")
