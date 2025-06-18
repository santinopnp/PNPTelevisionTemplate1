# run_bot.py

import logging
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def notify_kicked_users(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.message:
        await update.message.reply_text(
            "Has sido expulsado del canal por expiración de tu membresía. "
            "Puedes renovarla en cualquier momento para volver a ingresar. ✨"
        )


def main():
    try:
        from bot.config import BOT_TOKEN, ADMIN_IDS
        from bot.start import start_command, help_command
        from bot.admin import admin_command, stats_command, admin_help_command
        from bot.plans import plans_command
        from bot.callbacks import handle_callback
        from bot.utils.expiration_task import check_expired_users

        # logger.info(f"Bot Token: {BOT_TOKEN}")
        # logger.info(f"Admin IDs: {ADMIN_IDS}")

        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("plans", plans_command))
        app.add_handler(CommandHandler("admin", admin_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("admin_help", admin_help_command))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(
            MessageHandler(
                filters.StatusUpdate.LEFT_CHAT_MEMBER, notify_kicked_users
            )
        )

       if app.job_queue:
    app.job_queue.run_repeating(check_expired_users, interval=24 * 60 * 60)
else:
    print("WARNING: JobQueue not available - scheduled tasks disabled")

        print("✅ Bot starting...")
        app.run_polling(drop_pending_updates=True)

    except ModuleNotFoundError as e:
        if e.name == "asyncpg":
            print("❌ Error: asyncpg is not installed. Run 'pip install -r requirements.txt'")
        else:
            print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
