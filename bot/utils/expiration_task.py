import asyncio
from datetime import datetime
from telegram import Bot
from bot.config import BOT_TOKEN, CHANNELS
from bot.subscriber_manager import subscriber_manager

bot = Bot(token=BOT_TOKEN)

async def check_expired_users():
    expired_users = []
    now = datetime.now()

    for record in await subscriber_manager.get_all():
        exp_date = record["expires_at"]
        if exp_date < now:
            expired_users.append(record["user_id"])

    for user_id in expired_users:
        for channel in CHANNELS.values():
            try:
                await bot.ban_chat_member(chat_id=channel, user_id=user_id)
                await bot.unban_chat_member(chat_id=channel, user_id=user_id)
                print(f"Removed expired user: {user_id}")
            except Exception as e:
                print(f"Error removing {user_id}: {e}")
