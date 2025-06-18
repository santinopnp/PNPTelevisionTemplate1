# -*- coding: utf-8 -*-
"""Admin command handlers."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.texts import TEXTS
from bot.config import ADMIN_IDS, ADMIN_HOST, ADMIN_PORT
from bot.subscriber_manager import subscriber_manager

logger = logging.getLogger(__name__)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin command."""
    try:
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text(TEXTS["en"]["admin_only"])
            return

        stats = subscriber_manager.get_stats()
        keyboard = [
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("🌐 Web Panel", url=f"http://{ADMIN_HOST}:{ADMIN_PORT}")],
        ]
        text = (
            "🔧 **Admin Panel**\n\n"
            f"👥 Total users: {stats['total']}\n"
            f"✅ Active subscriptions: {stats['active']}\n"
            f"🌐 **Web Panel:** http://{ADMIN_HOST}:{ADMIN_PORT}"
        )
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in admin_command: {e}")
        await update.message.reply_text("❌ Error accessing admin panel")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    try:
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text(TEXTS["en"]["admin_only"])
            return

        stats = subscriber_manager.get_stats()
        text = (
            "📊 **Bot Statistics**\n\n"
            f"👥 Total users: {stats['total']}\n"
            f"✅ Active subscriptions: {stats['active']}\n"
            f"🌐 **Web Panel:** http://{ADMIN_HOST}:{ADMIN_PORT}"
        )
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await update.message.reply_text("❌ Error retrieving statistics")


async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /admin_help command."""
    try:
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text(TEXTS["en"]["admin_only"])
            return

        text = TEXTS["en"]["admin_help"]
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in admin_help_command: {e}")
        await update.message.reply_text("❌ Error retrieving help information")
