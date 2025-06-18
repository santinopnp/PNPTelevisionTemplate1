#!/usr/bin/env python3
"""
Simplified Subscription Bot for PNP Television.
Based on provided standalone script, integrated into repository structure.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# Bot configuration from environment
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_private_channel")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "PNP Television")

# Plan definitions
PLANS = {
    "week": {
        "name": "WEEK PASS",
        "price": "$14.99",
        "days": 7,
        "description": "Acceso total a PNP TV por 7 días 🔥"
    },
    "month": {
        "name": "MONTH PASS",
        "price": "$24.99",
        "days": 30,
        "description": "Un mes entero de placer visual sin límites 💦"
    },
    "3month": {
        "name": "3 MONTH PASS",
        "price": "$49.99",
        "days": 90,
        "description": "3 meses de acceso VIP. ¡Ahorra y disfruta más! 💎"
    },
    "halfyear": {
        "name": "1/2 YEAR PASS",
        "price": "$79.99",
        "days": 180,
        "description": "6 meses de acceso full a la experiencia PNP 🔥🔥"
    },
    "year": {
        "name": "1 YEAR PASS",
        "price": "$99.99",
        "days": 365,
        "description": "Todo un año con los shows más calientes de PNP 🖤"
    },
    "lifetime": {
        "name": "LIFETIME PASS",
        "price": "$199.99",
        "days": 3650,
        "description": "Acceso ilimitado y de por vida a todo el contenido 💀"
    }
}

# Payment links from environment
PAYMENT_LINKS = {
    "week": os.getenv("WEEK_PAYMENT_LINK", ""),
    "month": os.getenv("MONTH_PAYMENT_LINK", ""),
    "3month": os.getenv("3MONTH_PAYMENT_LINK", ""),
    "halfyear": os.getenv("HALFYEAR_PAYMENT_LINK", ""),
    "year": os.getenv("YEAR_PAYMENT_LINK", ""),
    "lifetime": os.getenv("LIFETIME_PAYMENT_LINK", "")
}

# Message templates
MESSAGES = {
    "welcome": f"""
🎬 Bienvenidx a **{CHANNEL_NAME}**

Tu portal exclusivo a la experiencia más intensa y provocadora de la red.

🌈 **¿Qué incluye tu suscripción?**
• Acceso a shows en vivo y grabados
• Performers calientes y sin censura
• Llamadas privadas y salas VIP
• Comunidad 24/7 en constante expansión

👉 Elige un plan para entrar al universo de PNP.
""",
    "subscription_status_active": "✅ Tu acceso a **PNP Television** está ACTIVO hasta el: {expiry_date}",
    "subscription_status_inactive": "🚫 No tienes una suscripción activa.\nActiva tu acceso para entrar a los canales privados 🔐",
    "plans_header": "💳 **Elige tu Pase PNP:**",
    "access_granted": """
🎉 Acceso confirmado

Tu pase **{plan_name}** ya está activo.

🔗 Aquí tienes tu enlace exclusivo. Úsalo solo tú:
👇👇👇
""",
    "help_text": """
🛠 **Centro de Soporte PNP**

Comandos disponibles:
• `/start` → Menú principal
• `/status` → Ver tu suscripción
• `/plans` → Ver opciones de pase

👑 Soporte directo: @soporte_pnptv
"""
}

# ---------------------------------------------------------------------------
# Data persistence helpers
# ---------------------------------------------------------------------------

def load_users() -> Dict:
    try:
        with open('data/users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users: Dict) -> bool:
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception:
        return False


def update_user(user_id: int, data: Dict) -> bool:
    users = load_users()
    user_key = str(user_id)
    if user_key not in users:
        users[user_key] = {
            "id": user_id,
            "created_at": datetime.now().isoformat(),
            "subscription_active": False,
            "subscription_until": None,
            "plan": None,
            "payments": 0
        }
    users[user_key].update(data)
    users[user_key]["last_updated"] = datetime.now().isoformat()
    return save_users(users)


def is_user_active(user_data: Dict) -> bool:
    try:
        expiry = datetime.fromisoformat(user_data.get('subscription_until', ''))
        return datetime.now() < expiry
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    update_user(user.id, {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": user.language_code
    })
    users = load_users()
    info = users.get(str(user.id), {})
    active = is_user_active(info)
    status_msg = (
        MESSAGES["subscription_status_active"].format(
            expiry_date=datetime.fromisoformat(info["subscription_until"]).strftime('%d/%m/%Y')
        ) if active else MESSAGES["subscription_status_inactive"]
    )
    keyboard = [
        [InlineKeyboardButton("💎 Ver Planes", callback_data="show_plans")],
        [InlineKeyboardButton("👤 Mi Estado", callback_data="my_status")],
        [InlineKeyboardButton("❓ Ayuda", callback_data="help")]
    ]
    if user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("👑 Admin", callback_data="admin_panel")])
    await update.message.reply_text(
        f"{MESSAGES['welcome']}\n\n{status_msg}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    message = MESSAGES["plans_header"]
    keyboard = []
    for plan_id, plan_info in PLANS.items():
        message += f"\n\n💳 *{plan_info['name']}* - {plan_info['price']}\n📝 {plan_info['description']}"
        keyboard.append([
            InlineKeyboardButton(
                f"{plan_info['name']} - {plan_info['price']}",
                callback_data=f"select_plan_{plan_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="back_to_start")])
    if query:
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = query.data.split("_")[-1]
    plan_info = PLANS.get(plan_id)
    if not plan_info:
        await query.edit_message_text("❌ Plan no válido")
        return
    payment_link = PAYMENT_LINKS.get(plan_id, "")
    instructions = f"""
💳 **Instrucciones de Pago**

📝 Plan: {plan_info['name']}
💰 Precio: {plan_info['price']}

1️⃣ Haz clic en el botón de pago
2️⃣ Finaliza tu compra en Bold.co
3️⃣ Envíanos el comprobante a @soporte_pnptv
4️⃣ Recibe tu acceso exclusivo al canal
"""
    keyboard = [
        [InlineKeyboardButton("💳 Pagar Ahora", url=payment_link)],
        [InlineKeyboardButton("🔙 Ver Otros Planes", callback_data="show_plans")]
    ]
    await query.edit_message_text(instructions, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(MESSAGES["help_text"], reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Ver Planes", callback_data="show_plans")],
            [InlineKeyboardButton("🔙 Volver", callback_data="back_to_start")]
        ]), parse_mode='Markdown')
    else:
        await update.message.reply_text(MESSAGES["help_text"], parse_mode='Markdown')


# ---------------------------------------------------------------------------
# Callback dispatcher
# ---------------------------------------------------------------------------

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    data = query.data
    if data == "show_plans":
        await show_plans(update, context)
    elif data.startswith("select_plan_"):
        await select_plan(update, context)
    elif data == "help":
        await show_help(update, context)
    elif data == "back_to_start":
        await start_command(update, context)


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bot entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN no configurado")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("plans", show_plans))
    app.add_handler(CommandHandler("help", show_help))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    logger.info("🤖 Simple subscription bot iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
