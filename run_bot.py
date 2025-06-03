import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# -*- coding: utf-8 -*-
import logging
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    try:
        from bot.config import BOT_TOKEN, ADMIN_IDS
        from bot.start import start_command, help_command
        from bot.admin import admin_command, stats_command, admin_help_command
        from bot.plans import plans_command
        from bot.callbacks import handle_callback

        logger.info(f"Bot Token: {BOT_TOKEN}")
        logger.info(f"Admin IDs: {ADMIN_IDS}")

        app = Application.builder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("plans", plans_command))
        app.add_handler(CommandHandler("admin", admin_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("admin_help", admin_help_command))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        print("✅ Bot starting...")
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()