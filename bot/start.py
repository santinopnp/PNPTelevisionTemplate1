# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from bot.texts import TEXTS


if __name__ == "__main__":
    print("This module provides Telegram command handlers and isn't intended "
          "to be executed directly.\n"
          "Run 'python run_bot.py' from the project root to start the bot.")
    exit(1)

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        user = update.effective_user
        logger.info(f"User {user.id} ({user.full_name}) started the bot")
        
        # Language selection keyboard
        keyboard = [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")
            ]
        ]
        
        welcome_text = (
            "📺 **Welcome to PNP Television Bot Ultimate!**\n"
            "Please choose your language:\n\n"
            "📺 **¡Bienvenido a PNP Television Bot Ultimate!**\n"
            "Por favor elige tu idioma:"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text(
            "❌ An error occurred. Please try again.\n"
            "❌ Ocurrio un error. Por favor intenta de nuevo."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    try:
        help_text = """📺 **PNP Television Bot Ultimate**

**Available Commands:**
/start - Start the bot and select language
/help - Show this help message
/plans - View subscription plans

**Features:**
✅ Multiple subscription plans
✅ Secure payment processing  
✅ Real-time admin panel
✅ Multi-language support
✅ Channel management

**Support:**
📧 Email: lex@pnptelevision.co
📱 Telegram: @PNPTVSupport

**Admin Panel:** http://localhost:8080"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await update.message.reply_text("❌ Error showing help")
