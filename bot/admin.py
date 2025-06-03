# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from bot.texts import TEXTS
from bot.config import ADMIN_IDS

logger = logging.getLogger(__name__)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    try:
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ This command is for administrators only.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Recent Users", callback_data="admin_users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🧹 Cleanup", callback_data="admin_cleanup")],
            [InlineKeyboardButton("🌐 Web Panel", url="http://localhost:8080")]
        ]
        
        text = """🔧 **Admin Panel**

Welcome to the admin panel!
Choose an option below:

🌐 **Web Panel:** http://localhost:8080
📊 **Database:** Local JSON
⏰ **Status:** Online"""
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in admin_command: {e}")
        await update.message.reply_text("❌ Error accessing admin panel")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    try:
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ This command is for administrators only.")
            return
        
        # Simple stats (you'll enhance this with real database)
        text = """📊 **Bot Statistics**

👥 Total users: 0
✅ Active subscriptions: 0
📅 New users today: 0
💰 Total revenue: $0.00

**Plan Distribution:**
• Trial: 0
• Monthly: 0
• VIP: 0
• Yearly: 0

🌐 **Web Panel:** http://localhost:8080"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")],
            [InlineKeyboardButton("🌐 Web Panel", url="http://localhost:8080")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await update.message.reply_text("❌ Error retrieving statistics")

async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_help command"""
    try:
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ This command is for administrators only.")
            return
        
        text = TEXTS['en']['admin_help']  # Use English by default for admin
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in admin_help_command: {e}")
        await update.message.reply_text("❌ Error retrieving help information")