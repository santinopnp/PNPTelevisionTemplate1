import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configuración de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token del bot (obtener de @BotFather)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

class BotMenus:
    @staticmethod
    def main_menu_keyboard():
        """Menú principal inline"""
        keyboard = [
            [InlineKeyboardButton("💎 PNP TV PRIME", callback_data='tv_prime')],
            [InlineKeyboardButton("📡 PNP Television Live", callback_data='live')],
            [InlineKeyboardButton("🎉 Cloud Nine Ball", callback_data='events')],
            [InlineKeyboardButton("⚖️ Legal / Legales", callback_data='legal')],
            [InlineKeyboardButton("📬 Contact / Contacto", callback_data='contact')]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def persistent_keyboard(is_premium=False):
        """Teclado persistente"""
        buttons = [
            [KeyboardButton("🤖 Cristina Crystal"), KeyboardButton("💳 Mi Membresía")]
        ]
        if is_premium:
            buttons.append([KeyboardButton("🎟️ Book a Private Show"), KeyboardButton("🎥 Join Private Show")])

        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

class BotHandlers:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        welcome_text = (
            "🧬 PNP TELEVISION ⬢ TELEGRAM COMMUNITY\n"
            "Let's get spun together! / ¡Vamos a ponernos cricos juntos!\n\n"
            "🎛️ Main Menu / Menú Principal\n"
            "Choose an option below / Elige una opción abajo:"
        )

        await update.message.reply_text(
            welcome_text,
            reply_markup=BotMenus.main_menu_keyboard()
        )

        # Teclado persistente
        await update.message.reply_text(
            "⬇️ Quick Access / Accesos Rápidos:",
            reply_markup=BotMenus.persistent_keyboard(is_premium=True)
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja callbacks de botones inline"""
        query = update.callback_query
        await query.answer()

        callback_handlers = {
            'tv_prime': self.show_tv_prime,
            'live': self.show_live,
            'events': self.show_events,
            'legal': self.show_legal,
            'contact': self.show_contact
        }

        handler = callback_handlers.get(query.data)
        if handler:
            await handler(query, context)

    async def show_tv_prime(self, query, context):
        text = (
            "💎 PNP TV PRIME — Contenido adulto amateur\n\n"
            "Subscription Options / Opciones de Suscripción:\n"
            "• ✈️ Trial Trip — $14.99 / 7 días\n"
            "• ☁️ Cloudy Month — $24.99 / 30 días\n"
            "• 🔁 Frequent Flyer — $39.99 / 2 meses\n"
            "• 🏄 Slam Surfer — $79.99 / 6 meses\n"
            "• 🌐 Full Year — $99.99 / 12 meses"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back / Atrás", callback_data='back_main')]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_live(self, query, context):
        text = (
            "📡 PNP Television Live\n\n"
            "Coming Soon! / ¡Próximamente!\n"
            "Exclusive real-time experiences with performers and the community.\n"
            "🔐 Only for active subscribers / Solo para suscriptores activos."
        )
        keyboard = [[InlineKeyboardButton("🔙 Back / Atrás", callback_data='back_main')]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_events(self, query, context):
        text = (
            "🎉 Cloud Nine Ball\n\n"
            "Coming Soon! / ¡Próximamente!\n"
            "Weekly themed multimedia hedonistic parties:\n"
            "- Tuesday: Música Malandra para Viciosos\n"
            "- Thursday: Smoke & Stroke\n"
            "- Saturday: DELIRIUM"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back / Atrás", callback_data='back_main')]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_contact(self, query, context):
        text = (
            "📬 Contact / Contacto\n\n"
            "💬 Chat with our team / Habla con el equipo\n"
            "🚩 Report inappropriate content / Reportar contenido\n"
            "👥 Join the main community group / Unirse al grupo principal"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back / Atrás", callback_data='back_main')]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def show_legal(self, query, context):
        text = (
            "⚖️ Legal / Legales\n\n"
            "📜 Terms & Conditions / Términos y Condiciones\n"
            "🔐 Privacy Policy / Política de Privacidad\n"
            "💸 Refunds / Reembolsos\n"
            "✅ Safe Consent Protocols / Protocolos de Consentimiento Seguro"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back / Atrás", callback_data='back_main')]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_persistent_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        responses = {
            "🤖 Cristina Crystal": "Hi! I'm Cristina, your virtual guide 💎 Ask me anything about PNP Television.",
            "💳 Mi Membresía": "You are currently subscribed to: Premium 🌟",
            "🎟️ Book a Private Show": "📅 Scheduling your private show via Webex... Check your calendar invite.",
            "🎥 Join Private Show": "🔗 Joining your private Webex session now..."
        }
        response = responses.get(text, "❓ Unknown command. Please use the menu.")
        await update.message.reply_text(response)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    handlers = BotHandlers()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CallbackQueryHandler(handlers.handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_persistent_buttons))

    print("🤖 Bot running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
